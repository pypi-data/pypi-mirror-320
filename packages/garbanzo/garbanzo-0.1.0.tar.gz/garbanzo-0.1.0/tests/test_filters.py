from beancount.core.data import Directive
from beancount.parser import parser
import pytest

from garbanzo.filter import EntryFilter, FixTransaction, RenameTransfers, trim_whitespace


def parse_entry(string: str) -> Directive:
    """Parses a single beancount entry from a string."""
    entries, errors, _ = parser.parse_string(string)
    assert len(entries) == 1
    assert not errors
    return entries[0]


# example filters

PIZZA_FILTER = FixTransaction.from_dict({
    "match": {
        "narration": "PIZZA"
    },
    "set": {
        "account": "Expenses:Restaurant:Pizza"
    }
})

CHARITY_FILTER = FixTransaction.from_dict({
    "match": {
        "narration": "HUMAN\\s*FUND"
    },
    "set": {
         "narration": "Donation",
         "payee": "The Human Fund",
         "account": "Expenses:Charity"
    }
})

STOCK_BUY_FILTER = FixTransaction.from_dict({
    "match": {
        "narration": "BUYMF|BUYSTOCK",
        "account_prefix": "Assets:Brokerage"
    },
    "set": {
        "narration": "Stock Buy"
    }
})

CHAINED_FILTER = EntryFilter.chain([PIZZA_FILTER, CHARITY_FILTER, STOCK_BUY_FILTER])

# example entries

PIZZA_TXN = parse_entry("""
2024-03-14 * "Vincent's Pizza"
  Liabilities:CreditCard:Visa -52.17 USD
  Expenses:Uncategorized       52.17 USD
""")

CHARITY_TXN = parse_entry("""
2024-12-23 * "HUMANFUND ORG"
  Assets:Bank:Checking    -1000.00 USD
  Expenses:Uncategorized   1000.00 USD
""")

STOCK_BUY_TXN = parse_entry("""
2024-12-27 * "BUYSTOCK"
  Assets:Brokerage:Cash     -1233.05 USD
  Assets:Brokerage:RothIRA         1 COKE {1233.05 USD}
""")

PRICE_ENTRY = parse_entry('2024-02-07 balance Assets:Checking  163.00 USD')


@pytest.mark.parametrize(['filt', 'old_entry', 'new_entry'], [
    (
        PIZZA_FILTER,
        PIZZA_TXN,
        parse_entry("""
2024-03-14 * "Vincent's Pizza"
  Liabilities:CreditCard:Visa  -52.17 USD
  Expenses:Restaurant:Pizza     52.17 USD
        """)
    ),
    (
        CHARITY_FILTER,
        CHARITY_TXN,
        parse_entry("""
2024-12-23 * "The Human Fund" "Donation"
  Assets:Bank:Checking  -1000.00 USD
  Expenses:Charity       1000.00 USD
        """)
    ),
    (
        STOCK_BUY_FILTER,
        STOCK_BUY_TXN,
        parse_entry("""
2024-12-27 * "Stock Buy"
  Assets:Brokerage:Cash     -1233.05 USD
  Assets:Brokerage:RothIRA         1 COKE {1233.05 USD}
        """)
    ),
    # no effect
    (
        PIZZA_FILTER,
        CHARITY_TXN,
        CHARITY_TXN
    ),
    # chain of filters
    (
        CHAINED_FILTER,
        CHARITY_TXN,
        parse_entry("""
2024-12-23 * "The Human Fund" "Donation"
  Assets:Bank:Checking  -1000.00 USD
  Expenses:Charity       1000.00 USD
        """)
    ),
    # mismatched types (no effect)
    (
        PIZZA_FILTER,
        PRICE_ENTRY,
        PRICE_ENTRY
    ),
    (
        CHAINED_FILTER,
        PRICE_ENTRY,
        PRICE_ENTRY
    ),
])
def test_fix_transaction(filt, old_entry, new_entry):
    """Tests that the application of a FixTransaction filter (or chain of them) has the expected effect on an entry."""
    assert isinstance(old_entry, type(new_entry))
    assert filt(old_entry) == new_entry


TXN_WITH_EXCESS_WHITESPACE = """
2025-01-01 * " PAYMENT TO   XYZ "
  Assets:Checking  -100 USD
  Assets:Savings    100 USD
"""

@pytest.mark.parametrize(['old_entry', 'new_entry'], [
    (
        parse_entry("""
2025-01-01 * " PAYMENT TO   XYZ "
  Assets:Checking         -100 USD
  Expenses:Uncategorized   100 USD"""),
        parse_entry("""
2025-01-01 * "PAYMENT TO XYZ"
  Assets:Checking         -100 USD
  Expenses:Uncategorized   100 USD"""),
    ),
    # no effect
    (PIZZA_TXN, PIZZA_TXN),
    (PRICE_ENTRY, PRICE_ENTRY),
])
def test_trim_whitespace(old_entry, new_entry):
    assert trim_whitespace(old_entry) == new_entry


ACCOUNT_NAME_MAP = {
    'Assets:Checking': 'Checking',
    'Assets:Savings': 'Savings',
    'Liabilities:CreditCard': 'Credit Card'
}


@pytest.mark.parametrize(['account_name_map', 'old_entry', 'new_entry'], [
    (
        ACCOUNT_NAME_MAP,
        parse_entry("""
2025-01-01 * "Online Transfer to xxxxx"
  Assets:Checking   -250 USD
  Assets:Savings     250 USD
        """),
        parse_entry("""
2025-01-01 * "Transfer: Checking -> Savings"
  Assets:Checking   -250 USD
  Assets:Savings     250 USD
        """)
    ),
    (
        ACCOUNT_NAME_MAP,
        parse_entry("""
2025-01-01 * "Web payment"
  Assets:Checking        -250 USD
  Liabilities:CreditCard  250 USD
        """),
        parse_entry("""
2025-01-01 * "Payment: Checking -> Credit Card"
  Assets:Checking        -250 USD
  Liabilities:CreditCard  250 USD
        """)
    ),
])
def test_rename_transfers(account_name_map, old_entry, new_entry):
    """Tests the RenameTransfers filter."""
    filt = RenameTransfers(account_name_map)
    assert filt(old_entry) == new_entry
