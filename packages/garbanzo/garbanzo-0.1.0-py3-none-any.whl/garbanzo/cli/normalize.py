from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Optional

from fancy_dataclass import CLIDataclass

from garbanzo import logger
from garbanzo.ledger import BeancountLedger


@dataclass
class ModifyLedgerCmd(CLIDataclass):
    """Base class for a subcommand that reads in a beancount ledger and modifies it in some way."""

    ledger_file: Path = field(metadata={'help': 'beancount ledger file'})
    inplace: bool = field(default=False, metadata={'help': 'modify files in place'})
    files: Optional[list[Path]] = field(default=None, metadata={'nargs': '+', 'help': 'subset of files to modify', 'metavar': 'FILE'})

    def __post_init__(self) -> None:
        if self.files is not None:
            self._check_files(self.ledger)

    def _check_files(self, ledger: BeancountLedger) -> None:
        """Checks that the list of files provided are among those included in the ledger.
        If not, raises a ValueError."""
        assert self.files is not None
        valid_paths = {path.resolve() for path in [ledger.path] + ledger.included_files}
        for path in self.files:
            assert isinstance(path, Path)
            if path.resolve() not in valid_paths:
                raise ValueError(f'File not found in ledger: {path}')

    @cached_property
    def ledger(self) -> BeancountLedger:
        return BeancountLedger.load_file(self.ledger_file)


@dataclass
class NormalizeCmd(ModifyLedgerCmd, command_name='normalize'):
    """Sort entries, normalize whitespace and currency alignment."""

    def run(self) -> None:
        logger.info(f'Normalizing ledger {self.ledger_file}')
        extension = None if self.inplace else '.norm.beancount'
        self.ledger.save(extension=extension, files=self.files)
