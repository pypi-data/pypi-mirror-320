from collections.abc import Iterable
import datetime
from pathlib import Path
from typing import IO, Any, Hashable, TypeVar


K = TypeVar('K', bound=Hashable)


def replace_dict_keys(d: dict[K, Any], key_map: dict[K, K]) -> dict[K, Any]:
    """Replaces keys in a dict with new ones, according to the given key_map.
    NOTE: it is required that key_map is one-to-one."""
    vals = list(key_map.values())
    if len(set(vals)) != len(vals):
        raise ValueError('key_map must be one-to-one')
    return {key_map.get(key, key): val for (key, val) in d.items()}


def get_relative_account_dir(account: str) -> Path:
    """Gets the (relative) subdirectory of the documents directory corresponding to the given account."""
    path = Path()
    for seg in account.strip().split(':'):
        path = path / seg
    return path


def string_is_date(string: str, date_format: str = '%Y-%m-%d') -> bool:
    """Checks if a string can be converted to a date."""
    try:
        _ = datetime.datetime.strptime(string, date_format)
        return True
    except ValueError:
        return False


def quote(val: Any) -> str:
    """Renders a value as a string in double quotes."""
    return f'"{val}"'


def write_lines(lines: Iterable[str], f: IO[str]) -> None:
    """Writes lines to a file."""
    for line in lines:
        print(line, file=f)
