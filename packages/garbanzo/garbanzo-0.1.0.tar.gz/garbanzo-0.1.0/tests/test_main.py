from pathlib import Path
import shutil

import pytest

from garbanzo.cli.main import GarbanzoCLI
from garbanzo.ledger import EXEMPT_OPTION_KEYS, BeancountLedger

from . import EXAMPLE_DIR


TRANSACTION_PATH = EXAMPLE_DIR / 'transactions.beancount'
FILTERED_TRANSACTION_PATH = EXAMPLE_DIR / 'transactions.filtered.beancount'
NORMALIZED_TRANSACTION_PATH = EXAMPLE_DIR / 'transactions.normalized.beancount'
FILTER_JSON_PATH = EXAMPLE_DIR / 'filters.json'
TRANSFER_PATH = EXAMPLE_DIR / 'transfers.beancount'
FILTERED_TRANSFER_PATH = EXAMPLE_DIR / 'transfers.filtered.beancount'
LEDGER_PATH = EXAMPLE_DIR / 'ledger.beancount'


def make_local_copy(tmpdir, path):
    """Makes a local copy of the given path, relative to a temporary directory.
    Returns the local path."""
    local_path = Path(tmpdir / path.name)
    shutil.copy(path, local_path)
    return local_path


@pytest.mark.parametrize(['ledger_path', 'filtered_path', 'extra_args', 'error'], [
    (TRANSACTION_PATH, FILTERED_TRANSACTION_PATH, ['--json-filters', str(FILTER_JSON_PATH)], None),
    (TRANSACTION_PATH, FILTERED_TRANSACTION_PATH, ['--filters', '--json-filters', str(FILTER_JSON_PATH)], None),
    (TRANSFER_PATH, FILTERED_TRANSFER_PATH, [], None),
    (TRANSFER_PATH, None, ['--filters'], 'No filters provided'),
])
def test_filter(tmpdir, caplog, ledger_path, filtered_path, extra_args, error):
    """Tests the filter subcommand."""
    # make temporary copy of ledger file
    ledger_path_copy = make_local_copy(tmpdir, ledger_path)
    args = ['filter', str(ledger_path_copy)] + extra_args
    if error:  # expect error
        with pytest.raises(SystemExit):
            GarbanzoCLI.main(args)
        assert error in caplog.text
    else:
        filt_str = filtered_path.read_text()
        GarbanzoCLI.main(args)
        assert filt_str == ledger_path_copy.with_suffix('.filt.beancount').read_text()
        args = ['filter', str(ledger_path_copy), '--inplace'] + extra_args
        GarbanzoCLI.main(args)
        assert filt_str == ledger_path_copy.read_text()


def test_normalize_invalid_file(caplog):
    """Tests the normalize subcommand on a file that doesn't exist."""
    args = ['normalize', 'fake_ledger.beancount']
    try:
        GarbanzoCLI.main(args)
    except SystemExit as e:
        assert e.code == 1  # noqa: PT017
        assert 'File not found: fake_ledger.beancount' in caplog.text
    else:  # pragma: no cover
        pytest.fail('expected error')


def test_normalize_single(tmpdir):
    """Tests the normalize subcommand on a single transaction file."""
    norm_str = NORMALIZED_TRANSACTION_PATH.read_text()
    transaction_path = make_local_copy(tmpdir, TRANSACTION_PATH)
    args = ['normalize', str(transaction_path)]
    GarbanzoCLI.main(args)
    assert norm_str == transaction_path.with_suffix('.norm.beancount').read_text()
    args = ['normalize', str(transaction_path), '--inplace']
    GarbanzoCLI.main(args)
    assert norm_str == transaction_path.read_text()


def test_normalize_multi(tmpdir):
    """Tests the normalize subcommand on a top-level ledger file with options/plugins/includes."""
    ledger_path = make_local_copy(tmpdir, LEDGER_PATH)
    transaction_path = make_local_copy(tmpdir, TRANSACTION_PATH)
    ledger = BeancountLedger.load_file(ledger_path)
    assert not ledger.errors
    args = ['normalize', str(ledger_path)]
    GarbanzoCLI.main(args)
    norm_ledger_path = ledger_path.with_suffix('.norm.beancount')
    assert norm_ledger_path.exists()
    assert transaction_path.with_suffix('.norm.beancount').exists()
    norm_ledger = BeancountLedger.load_file(norm_ledger_path)
    assert not norm_ledger.errors
    assert len(ledger.entries) == len(norm_ledger.entries)
    # test entries are equivalent up to filenames
    def _fix_entry(entry):
        if hasattr(entry, 'postings'):
            postings = [posting._replace(meta=None) for posting in entry.postings]
            entry = entry._replace(postings=postings)
        return entry._replace(meta=None)
    assert list(map(_fix_entry, ledger.entries)) == list(map(_fix_entry, norm_ledger.entries))
    # test options_maps are equal (for non-exempt keys)
    opts1 = {key: val for (key, val) in ledger.options_map.items() if (key not in EXEMPT_OPTION_KEYS)}
    opts2 = {key: val for (key, val) in norm_ledger.options_map.items() if (key not in EXEMPT_OPTION_KEYS)}
    assert opts1 == opts2
    # test plugins are equal
    assert ledger.options_map['plugin'] == norm_ledger.options_map['plugin'] == [('beancount.plugins.auto_accounts', None)]


def test_normalize_subset(tmpdir, caplog):
    """Tests the normalize subcommand on a top-level ledger file with options/includes, but only modify an included file."""
    ledger_path = make_local_copy(tmpdir, LEDGER_PATH)
    transaction_path = make_local_copy(tmpdir, TRANSACTION_PATH)
    ledger = BeancountLedger.load_file(ledger_path)
    assert not ledger.errors
    args = ['normalize', str(ledger_path), '--files', str(transaction_path)]
    GarbanzoCLI.main(args)
    # top-level file was not normalized
    assert not ledger_path.with_suffix('.norm.beancount').exists()
    # transaction file was normalized
    norm_transaction_path = transaction_path.with_suffix('.norm.beancount')
    assert NORMALIZED_TRANSACTION_PATH.read_text() == norm_transaction_path.read_text()
    # include invalid file
    args = ['normalize', str(ledger_path), '--files', str(transaction_path), 'fake_file.beancount']
    with pytest.raises(SystemExit):
        GarbanzoCLI.main(args)
    assert 'File not found in ledger: fake_file.beancount' in caplog.text
