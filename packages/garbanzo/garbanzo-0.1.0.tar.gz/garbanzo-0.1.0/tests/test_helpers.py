from pathlib import Path

import pytest

from garbanzo.helpers import get_relative_account_dir, replace_dict_keys, string_is_date


def test_replace_dict_keys():
    d = {'a': 1, 'b': 2}
    assert replace_dict_keys(d, {'a': 'A', 'c': 'C'}) == {'A': 1, 'b': 2}
    with pytest.raises(ValueError, match='one-to-one'):
        _ = replace_dict_keys(d, {'a': 'A', 'c': 'A'})

@pytest.mark.parametrize('account', [
    '',
    'Assets',
    'Assets:Bank',
    'Assets:Bank:RothIRA',
])
def test_get_relative_account_dir(account):
    path = Path('/'.join(account.split(':')))
    assert get_relative_account_dir(account) == path

@pytest.mark.parametrize(['string', 'is_date'], [
    ('2025-01-01', True),
    ('2025-1-01', True),
    ('2025-1-1', True),
    ('', False),
    ('01/01/2025', False),
])
def test_string_is_date(string, is_date):
    assert string_is_date(string) == is_date
