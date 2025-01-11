from collections import defaultdict
from collections.abc import Sequence
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional, Self

from beancount import loader
import beancount.core.data
from beancount.core.data import Directive, Open, Transaction
from beancount.parser import options
from beancount.parser.grammar import ParserSyntaxError
from beancount.parser.lexer import LexerError

from garbanzo import logger
from garbanzo.helpers import quote, write_lines


# function to modify a BeancountLedger (immutably)
LedgerTransform = Callable[['BeancountLedger'], 'BeancountLedger']

# option keys not to include when writing out options to ledger file
EXEMPT_OPTION_KEYS = {'dcontext', 'filename', 'include', 'input_hash', 'plugin'}


def has_valid_beancount_extension(path: Path) -> bool:
    """Returns True if the given path has a valid extension for a beancount file."""
    return path.suffix.lower() in ['.beancount', '.bean']


def _apply_file_extension(filename: str, extension: str) -> str:
    """Applies an extension to a filename string."""
    return str(Path(filename).with_suffix(extension))


LEDGER_FATAL_ERR_TYPES = (
    LexerError,
    loader.LoadError,
    ParserSyntaxError,
)


def _ledger_error_is_fatal(error: object) -> bool:
    """Returns True if an error should be considered fatal when parsing a beancount ledger."""
    if isinstance(error, LEDGER_FATAL_ERR_TYPES):
        return True
    return False


class LedgerError(ValueError):
    """Error type for when a ledger can't be parsed or has a fatally invalid entry."""


def _write_normalized_entries_to_file(output_path: Path, entries: list[object]) -> None:
    """Writes ledger entries to a file in a normalized format (first sorting the entries)."""
    entries = beancount.core.data.sorted(entries)
    with open(output_path, 'w') as f:
        beancount.parser.printer.print_entries(entries, file=f)


@dataclass
class BeancountLedger:
    """Data structure storing data loaded from a beancount ledger."""

    path: Path  # top-level ledger path
    entries: list[Directive]
    errors: list[object]
    options_map: dict[str, Any]

    @property
    def num_entries(self) -> int:
        """Gets the number of entries."""
        return len(self.entries)

    @staticmethod
    def handle_ledger_errors(errors: list[object]) -> None:
        """Processes a list of errors encountered when parsing a ledger.
        If any is fatal, raises the first such a one as a LedgerError."""
        if errors:
            logger.warning(f'{len(errors)} error(s) found', extra={'highlighter': None})
        for err in errors:
            if _ledger_error_is_fatal(err):
                filename = err.source['filename']  # type: ignore[attr-defined]
                msg = f'error parsing {filename}'
                if hasattr(err, 'message'):
                    msg += f' - {err.message}'
                raise LedgerError(msg)

    @classmethod
    def load_file(cls, ledger_path: str | Path) -> Self:
        """Loads ledger data from a file."""
        path = Path(ledger_path)
        if not has_valid_beancount_extension(path):
            raise ValueError(f'{path} is not a valid beancount file')
        if not path.exists():
            raise ValueError(f'File not found: {path}')
        entries, errors, options_map = loader.load_file(path)
        cls.handle_ledger_errors(errors)
        return cls(path, entries, errors, options_map)

    def get_directives_of_type(self, tp: type[Directive]) -> list[Directive]:
        """Gets a list of all directives of the given type."""
        return [entry for entry in self.entries if isinstance(entry, tp)]

    def num_directives_of_type(self, tp: type[Directive]) -> int:
        """Gets the number of directives of the given type."""
        return sum(1 for entry in self.entries if isinstance(entry, tp))

    @property
    def open_directives(self) -> list[Directive]:
        """Gets a list of all Open directives, which store account information."""
        return self.get_directives_of_type(Open)

    @property
    def num_accounts(self) -> int:
        """Gets the number of accounts in the ledger.
        NOTE: this includes accounts that are closed."""
        return self.num_directives_of_type(Open)

    @property
    def num_transactions(self) -> int:
        """Gets the number of transactions in the ledger."""
        return self.num_directives_of_type(Transaction)

    def apply_file_extension(self, extension: str) -> 'BeancountLedger':
        """Returns a new BeancountLedger where all file paths have the given extension applied."""
        path = self.path.with_suffix(extension)
        entries = []
        for entry in self.entries:
            entry = deepcopy(entry)
            if entry.meta and (filename := entry.meta.get('filename')):
                entry.meta['filename'] = _apply_file_extension(filename, extension)
            entries.append(entry)
        # TODO: change paths in errors too?
        options_map = deepcopy(self.options_map)
        if filename := options_map.get('filename'):
            options_map['filename'] = _apply_file_extension(filename, extension)
        if includes := options_map.get('include'):
            assert isinstance(includes, list)
            options_map['include'] = [_apply_file_extension(filename, extension) for filename in includes]
        return BeancountLedger(path, entries, deepcopy(self.errors), options_map)

    @property
    def non_default_options(self) -> dict[str, Any]:
        """Gets the subset of options_map that does not match the beancount defaults."""
        defaults = options.OPTIONS_DEFAULTS
        return {key: val for (key, val) in self.options_map.items() if (val != defaults.get(key))}

    @property
    def included_files(self) -> list[Path]:
        """Gets the list of files included in the ledger."""
        includes = self.options_map.get('include', [])
        return [path for filename in includes if ((path := Path(filename)) != self.path.resolve())]

    @property
    def _non_default_option_directives(self) -> list[str]:
        """Gets option directives to append to the top-level ledger file (only for options that do not match the beancount defaults)."""
        lines = []
        if options_map := self.non_default_options:
            options_map = {key: val for (key, val) in options_map.items() if (key not in EXEMPT_OPTION_KEYS) and val}
            for key, val in options_map.items():
                line = 'option ' + quote(key)
                if isinstance(val, list):
                    line += ' '.join(map(quote, val))
                else:
                    line += quote(val)
                lines.append(line)
        return lines

    @property
    def _plugin_directives(self) -> list[str]:
        """Gets the list of plugin directives to append to the top-level ledger file."""
        lines = []
        for plugin, config_str in self.options_map.get('plugin', []):
            line = f'plugin "{plugin}"'
            if config_str:
                line += ' ' + quote(config_str)
            lines.append(line)
        return lines

    @property
    def _include_directives(self) -> list[str]:
        """Gets the list of include directives to append to the top-level ledger file."""
        lines = []
        if includes := self.included_files:
            for filename in includes:
                lines.append('include ' + quote(filename))
        return lines

    def save(self, extension: Optional[str] = None, files: Optional[list[Path]] = None) -> None:
        """Saves the ledger contents to one or more files.
        Each entry is saved to its associated filename.
        If an extension is provided, applies this extension to each file.
        If a list of files is provided (which are all included in the ledger), only saves files corresponding to these ones."""
        ledger = self if (extension is None) else self.apply_file_extension(extension)
        if files is None:
            valid_paths = None
        else:
            valid_paths = {path.resolve() for path in files}
            if extension:
                valid_paths = {path.with_suffix(extension) for path in valid_paths}
        is_valid_path: Callable[[Path], bool] = lambda path: (valid_paths is None) or (path.resolve() in valid_paths)
        entries_by_path = defaultdict(list)
        for entry in ledger.entries:
            path = Path(entry.meta['filename'])
            # exclude paths that are not in the specified subset
            if is_valid_path(path):
                entries_by_path[path].append(entry)
        logger.info('Saving ledger file(s)', extra={'highlighter': None})
        for path in sorted(entries_by_path):
            logger.info(f'    {path}')
            _write_normalized_entries_to_file(path, entries_by_path[path])
        if is_valid_path(ledger.path):
            # if there are options/plugins/includes, append them to the top-level ledger file
            with open(ledger.path, 'a') as f:
                for lines in [self._non_default_option_directives, self._plugin_directives, self._include_directives]:
                    if lines:
                        print('', file=f)
                        write_lines(lines, f)

    def apply_transforms(self, transforms: Sequence[LedgerTransform]) -> 'BeancountLedger':
        """Applies a sequence of transforms to a beancount ledger."""
        ledger = self
        if transforms:
            for transform in transforms:
                ledger = transform(ledger)
            if not ledger.entries:
                logger.warning('All entries were filtered out.')
        return ledger
