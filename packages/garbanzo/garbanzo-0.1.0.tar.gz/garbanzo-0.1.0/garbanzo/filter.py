from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field
from functools import reduce
import json
import operator
from pathlib import Path
import re
from typing import Any, Callable, Generic, Optional, Self, TypeVar, cast

from beancount.core.data import Account, Directive, Posting, Transaction
from fancy_dataclass import JSONDataclass

from garbanzo.helpers import replace_dict_keys
from garbanzo.ledger import BeancountLedger, LedgerTransform


S = TypeVar('S')
T = TypeVar('T', bound=Directive)

FilterFunc = Callable[[T], Optional[T]]
PredFunc = Callable[[T], bool]


###########
# HELPERS #
###########


class _Unset:
    """Sentinel value indicating to set a field's value to None."""


UNSET = _Unset()


def _none_if_unset(obj: Optional[S] | _Unset) -> Optional[S]:
    if obj == UNSET:
        return None
    return cast(Optional[S], obj)


# identity function
identity = lambda obj: obj


##############
# FILTER API #
##############


class BaseEntryFilter(ABC):
    """Filters a list of entries.
    This takes each entry and either filters it out (by returning None) or alters it (by returning a new entry)."""

    @abstractmethod
    def __call__(self, entry: Directive) -> Optional[Directive]:
        """Given an entry, returns None if the entry is to be removed, and a new entry if it is to be modified."""


class EntryFilter(BaseEntryFilter, Generic[T]):
    """Concrete implementation of an entry filter.
    This wraps a user-provided filter function, which takes an entry and returns an (optional) entry."""

    def __init__(self, func: FilterFunc[T]) -> None:
        self.func = func

    def __call__(self, entry: Directive) -> Optional[Directive]:
        """Calls the user-defined function on an entry."""
        assert isinstance(entry, Directive)
        return self.func(cast(T, entry))

    def __rshift__(self, other: Self) -> EntryFilter[T]:
        """Sequential composition of filters.
        filter1 >> filter2 means to apply filter1 first, then pass the output (if not None) to filter2."""

        def _composed(entry: T) -> Optional[T]:
            val = self(entry)
            if val is None:
                return None
            return other(val)

        return EntryFilter(_composed)

    @classmethod
    def chain(cls, filters: Sequence[EntryFilter[T]]) -> EntryFilter[T]:
        """Chains together multiple EntryFilters into a single filter by applying them sequentially."""
        return ChainedEntryFilter(list(filters))


@dataclass
class ChainedEntryFilter(EntryFilter[T]):
    """An EntryFilter consisting of a chain of EntryFilters applied sequentially."""

    filters: list[EntryFilter[T]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.filters:
            func: FilterFunc[T] = reduce(operator.rshift, self.filters)
        else:
            func = identity
        super().__init__(func)


class TransactionFilter(EntryFilter[Transaction]):
    """Specialization of EntryFilter for Transactions."""

    def __call__(self, entry: Directive) -> Optional[Directive]:
        """If the entry is a Transaction, call the filter funciton; otherwise leave it alone."""
        if isinstance(entry, Transaction):
            return self.func(entry)
        assert isinstance(entry, Directive)
        return entry


class BaseEntryPredicate(ABC):
    """A predicate (bool-valued function) on entries."""

    @abstractmethod
    def __call__(self, entry: Directive) -> bool:
        """Given an entry, returns True or False indicating whether the entry satisfies the predicate."""


class EntryPredicate(BaseEntryPredicate, Generic[T]):
    """Concrete implementation of an entry predicate.
    This wraps a user-provided predicate function, which takes an entry and returns True or False."""

    pred: Optional[PredFunc[T]] = None

    def __init__(self, pred: PredFunc[T]) -> None:
        self.pred = pred

    def __call__(self, entry: Directive) -> bool:
        """Calls the user-defined predicate on an entry."""
        assert self.pred is not None
        assert isinstance(entry, Directive)
        return self.pred(cast(T, entry))

    def __and__(self, other: EntryPredicate[T]) -> EntryPredicate[T]:
        """Takes the conjunction (logical AND) of two EntryPredicates."""

        def _pred(entry: T) -> bool:
            return self(entry) and other(entry)

        return EntryPredicate(_pred)

    def __or__(self, other: EntryPredicate[T]) -> EntryPredicate[T]:
        """Takes the disjunction (logical OR) of two EntryPredicates."""

        def _pred(entry: T) -> bool:
            return self(entry) or other(entry)

        return EntryPredicate(_pred)

    def __invert__(self) -> EntryPredicate[T]:
        """Takes the complement (logical NOT) of an EntryPredicate."""

        def _pred(entry: T) -> bool:
            return not self(entry)

        return EntryPredicate(_pred)

    def to_entry_filter(self) -> EntryFilter[T]:
        """Converts the EntryPredicate into an EntryFilter.
        This will take an entry and return the same entry if the predicate is satisfied, and None otherwise."""

        def _func(entry: T) -> Optional[T]:
            return entry if self(entry) else None

        return EntryFilter(_func)


class TransactionPredicate(EntryPredicate[Transaction]):
    """Specialization of EntryPredicate for Transactions."""


def filter_transform(filt: BaseEntryFilter | Callable[[BeancountLedger], BaseEntryFilter]) -> LedgerTransform:
    """Wraps a BaseEntryFilter into a LedgerTransform that applies the filter to each entry."""

    def _transform(ledger: BeancountLedger) -> BeancountLedger:
        if isinstance(filt, BaseEntryFilter):
            entry_filter = filt
        else:
            # assume that filt is a function that takes a ledger and returns a BaseEntryFilter
            entry_filter = filt(ledger)
        entries = []
        for entry in ledger.entries:
            entry = entry_filter(entry)
            # TODO: count number of entries?
            if entry is not None:
                entries.append(entry)
        return BeancountLedger(ledger.path, entries, [], ledger.options_map)

    return _transform


############
# MATCHING #
############


def _field_matches_regex(field: str, regex: str, flag: re.RegexFlag = re.IGNORECASE) -> PredFunc[object]:
    r = re.compile(regex, flag)

    def _pred(obj: object) -> bool:
        val = getattr(obj, field)
        return isinstance(val, str) and bool(r.findall(val))

    return _pred


@dataclass
class FieldMatchesRegex(EntryPredicate[T]):
    """Checks if a certain field of an Entry matches a particular regular expression."""

    field: str
    regex: str
    flag: re.RegexFlag = re.IGNORECASE

    def __post_init__(self) -> None:
        super().__init__(_field_matches_regex(self.field, self.regex, self.flag))


@dataclass
class HasAccountPrefix(TransactionPredicate):
    """Checks if any posting has an account that starts with a particular prefix."""

    account_prefix: str

    def __post_init__(self) -> None:
        def _pred(txn: Transaction) -> bool:
            return any(posting.account.startswith(self.account_prefix) for posting in txn.postings)

        super().__init__(_pred)


@dataclass
class HasAccountPrefixes(TransactionPredicate):
    """Checks if any posting has an account that starts with each prefix in a list of prefixes."""

    account_prefixes: list[str]

    def __post_init__(self) -> None:
        if not self.account_prefixes:
            raise ValueError('must provide at least one account prefix')
        # take the conjunction of HasAccountPrefix predicate for each prefix
        pred = reduce(operator.and_, map(HasAccountPrefix, self.account_prefixes))
        super().__init__(pred)


##########
# UPDATE #
##########


@dataclass
class AssignField(EntryFilter[T]):
    """Assigns a field to some value."""

    field: str  # name of the field
    value: T  # value to assign

    def __post_init__(self) -> None:
        kwargs = {self.field: self.value}
        super().__init__(lambda entry: entry._replace(**kwargs))


@dataclass
class AssignAccount(TransactionFilter):
    """Given a Transaction, if it has a unique posting whose account begins with account_prefix, will change the account of the posting to the given one."""

    account_prefix: str
    account: str

    def __post_init__(self) -> None:
        assert self.account.startswith(self.account_prefix)
        posting_matches_prefix: PredFunc[Posting] = lambda posting: posting.account.startswith(self.account_prefix)

        def _assign(txn: Transaction) -> Optional[Transaction]:
            valid_postings = list(filter(posting_matches_prefix, txn.postings))
            if len(valid_postings) == 1:
                postings = [posting._replace(account=self.account) if posting_matches_prefix(posting) else posting for posting in txn.postings]
                return txn._replace(postings=postings)
            return txn

        super().__init__(_assign)


@TransactionFilter
def trim_whitespace(txn: Transaction) -> Optional[Transaction]:
    """Remove excess whitespace from narration and payee fields."""
    kwargs = {}
    for key in ['narration', 'payee']:
        val = getattr(txn, key)
        if val is not None:
            kwargs[key] = ' '.join(val.strip().split())
    return txn._replace(**kwargs) if kwargs else txn


################
# JSON FILTERS #
################


class JSONTransactionFilter(TransactionFilter, JSONDataclass, store_type='off'):  # type: ignore[misc]
    """Subclass of TransactionFilter using JSON-specified criteria."""


class JSONTransactionPredicate(TransactionPredicate, JSONDataclass, store_type='off'):  # type: ignore[misc]
    """Subclass of TransactionFilter using JSON-specified criteria."""


@dataclass
class TransactionMatch(JSONTransactionPredicate, suppress_none=True):
    """Class for matching a Transaction based on JSON-specified criteria."""

    narration: Optional[str] = None  # regex to match narration
    payee: Optional[str] = None  # regex to match payee
    account_prefixes: Optional[list[str]] = None  # account prefixes to match

    def __post_init__(self) -> None:
        preds: list[PredFunc[Transaction]] = []
        for fld in ['narration', 'payee']:
            val = getattr(self, fld)
            if val is not None:
                preds.append(FieldMatchesRegex(fld, val))
        if self.account_prefixes is not None:
            preds.append(HasAccountPrefixes(self.account_prefixes))
        if preds:
            pred: PredFunc[Transaction] = reduce(operator.and_, preds)
        else:
            pred = lambda _: True
        super().__init__(pred)


@dataclass
class TransactionUpdate(JSONTransactionFilter, suppress_none=True):
    """Class for updating a Transaction based on JSON-specified criteria."""

    # narration to set
    narration: Optional[_Unset | str] = None
    # payee to set
    payee: Optional[_Unset | str] = None
    # tags to set
    tags: Optional[_Unset | list[str]] = None
    # links to set
    links: Optional[_Unset | list[str]] = None
    # account to set (for a unique posting matching this account type)
    # For example, if the value is 'Expenses:Food:Restaurants', this will set an 'Expense' posting to this specific account, provided there is a unique posting with the 'Expense' prefix.
    account: Optional[str] = None

    def __post_init__(self) -> None:
        filters: list[EntryFilter[Transaction]] = []
        for fld in ['narration', 'payee', 'tags', 'links']:
            # If value is None, leave the field alone.
            # If UNSET, set it to None.
            if (value := getattr(self, fld)) is not None:
                value = _none_if_unset(value)
                filters.append(AssignField(fld, value))
        if self.account is not None:
            account_prefix = self.account.split(':')[0]
            filters.append(AssignAccount(account_prefix, self.account))
        super().__init__(ChainedEntryFilter(filters))

    def to_dict(self, **kwargs: Any) -> dict[str, Any]:  # noqa: D102
        d = super().to_dict(**kwargs)
        # NOTE: we interpret UNSET as JSON null, and None as a missing field
        for fld in ['narration', 'payee']:
            if getattr(self, fld) == UNSET:
                d[fld] = None
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any], **kwargs: Any) -> Self:  # noqa: D102
        # NOTE: we interpret JSON null as UNSET, and a missing field as None
        d2 = {key: UNSET if (val is None) else val for (key, val) in d.items()}
        return super().from_dict(d2, **kwargs)


@dataclass
class FixTransaction(JSONTransactionFilter):
    """Given a Transaction, if it matches the "match" criteria, applies the "set" criteria.
    The criteria can be specified with a JSON blob with "match" and "set" keys."""

    match_: TransactionMatch
    set: TransactionUpdate

    @staticmethod
    def _fix_dict(d: dict[str, Any]) -> dict[str, Any]:
        return {('match' if (key == 'match_') else key): val for (key, val) in d.items()}

    def to_dict(self, **kwargs: Any) -> dict[str, Any]:  # noqa: D102
        return replace_dict_keys(super().to_dict(**kwargs), {'match_': 'match'})

    @classmethod
    def from_dict(cls, d: dict[str, Any], **kwargs: Any) -> Self:  # noqa: D102
        d = replace_dict_keys(d, {'match': 'match_'})
        return super().from_dict(d, **kwargs)

    def __post_init__(self) -> None:
        def _func(txn: Transaction) -> Optional[Transaction]:
            if self.match_(txn):  # if transaction matches, apply the update
                return self.set(txn)
            # otherwise leave the transaction alone
            return txn

        super().__init__(_func)


def load_json_filters(json_path: Path) -> list[FixTransaction]:
    """Loads a JSON file containing a list of parameter objects that can be converted to FixTransaction objects, and returns the list of such objects."""
    with open(json_path) as f:
        obj_list = json.load(f)
    err = 'JSON file must contain a list of JSON objects'
    assert isinstance(obj_list, list), err
    assert all(isinstance(obj, dict) for obj in obj_list), err
    filters = []
    for obj in obj_list:
        filters.append(FixTransaction.from_dict(obj))
    return filters


#############
# TRANSFERS #
#############


@dataclass
class RenameTransfers(TransactionFilter):
    """Sets the narration of any "transfer" transaction in a consistent format, "TYPE: SRC_NAME -> DEST_NAME".

    A transfer is any transaction consisting of two postings, each of whose account is in account_name_map, which maps from each account to its name.
    TYPE is "Transfer" if the destination account is an Asset, and "Payment" if the destination account is a Liability.
    SRC_NAME is the name associated with the source account.
    DEST_NAME is the name associated with the destination account."""

    account_name_map: dict[Account, str]

    def __post_init__(self) -> None:
        name_map = self.account_name_map

        def _rename_transfer(txn: Transaction) -> Optional[Transaction]:
            postings = txn.postings
            if (len(postings) == 2) and all(posting.account in name_map for posting in postings):
                # first account is the source (the one that was debited)
                if postings[0].units.number < 0:
                    src, dest = postings[0].account, postings[1].account
                else:
                    src, dest = postings[1].account, postings[0].account
                if dest.startswith('Assets'):
                    label = 'Transfer'
                elif dest.startswith('Liabilities'):
                    label = 'Payment'
                else:  # no valid label
                    return txn
                src_name = name_map[src]
                dest_name = name_map[dest]
                narration = f'{label}: {src_name} -> {dest_name}'
                return txn._replace(narration=narration)
            return txn

        super().__init__(_rename_transfer)

    @classmethod
    def from_ledger(cls, ledger: BeancountLedger) -> Self:
        """Constructs a RenameTransfers filter from a BeancountLedger by constructing the account_name_map from the set of all Open directives specifying a "name" metadata field."""
        account_name_map = {}
        for entry in ledger.open_directives:
            if entry.meta and ('name' in entry.meta):
                account = entry.account
                name = entry.meta['name']
                if account.startswith('Assets') or account.startswith('Liabilities'):
                    account_name_map[account] = name
        return cls(account_name_map)


rename_transfers = filter_transform(RenameTransfers.from_ledger)
