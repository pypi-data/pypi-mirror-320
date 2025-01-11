from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from beancount.core.data import Directive

from garbanzo import logger
from garbanzo.cli.normalize import ModifyLedgerCmd
from garbanzo.filter import EntryFilter, filter_transform, load_json_filters, rename_transfers, trim_whitespace
from garbanzo.ledger import LedgerTransform


# map from filter names to filters (as LedgerTransforms)
FILTERS: dict[str, LedgerTransform] = {
    'rename_transfers': rename_transfers,
    'trim_whitespace': filter_transform(trim_whitespace),
}

# map from filter names to descriptions
FILTER_DESCRS: dict[str, str] = {
    'rename_transfers': 'use consistent format for narration of "transfer" transactions, based on "name" account metadata',
    'trim_whitespace': 'remove excess whitespace from narration and payee',
}

# list of filters to use by default
DEFAULT_FILTERS = [
    'rename_transfers',
    'trim_whitespace',
]

_FILTER_DESCR = '\n'.join(f'    {name}: {descr}' for (name, descr) in FILTER_DESCRS.items())
_FILTER_DESCR += '\n(default: ' + ', '.join(DEFAULT_FILTERS) + ')'


@dataclass
class FilterCmd(ModifyLedgerCmd, command_name='filter'):
    """Apply one or more filters to remove or modify ledger entries."""

    filters: list[str] = field(default_factory=lambda: DEFAULT_FILTERS, metadata={'nargs': '*', 'choices': list(FILTERS), 'help': f'filters to apply\n{_FILTER_DESCR}'})
    # TODO: store JSON paths within ledger metadata to avoid using a special command-line argument here
    json_filters: list[Path] = field(default_factory=list, metadata={'nargs': '+', 'help': 'one or more JSON files containing a list of filters'})

    def get_json_filter(self) -> Optional[EntryFilter[Directive]]:
        """Gets a single EntryFilter object used to filter ledger entries."""
        filters: list[EntryFilter[Directive]] = []
        for json_path in self.json_filters:
            filters.extend(load_json_filters(json_path))
        return EntryFilter.chain(filters) if filters else None

    def run(self) -> None:
        logger.info(f'Filtering ledger {self.ledger_file}')
        if self.filters:
            filter_str = ', '.join(self.filters)
            logger.info(f'Using filters: {filter_str}')
        if self.json_filters:
            json_strs = ', '.join(map(str, self.json_filters))
            logger.info(f'Using filters from {json_strs}')
        transforms = [FILTERS[name] for name in self.filters]
        json_filter = self.get_json_filter()
        if json_filter is not None:
            transforms.append(filter_transform(json_filter))
        if not transforms:
            raise ValueError('No filters provided.')
        logger.info(f'Pre-filter:  {self.ledger.num_entries} entries, {self.ledger.num_transactions} transactions')
        ledger = self.ledger.apply_transforms(transforms)
        logger.info(f'Post-filter: {ledger.num_entries} entries, {ledger.num_transactions} transactions')
        extension = None if self.inplace else '.filt.beancount'
        ledger.save(extension=extension, files=self.files)
