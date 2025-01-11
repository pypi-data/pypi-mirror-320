# Garbanzo

[![PyPI - Version](https://img.shields.io/pypi/v/garbanzo)](https://pypi.org/project/garbanzo)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/jeremander/garbanzo/workflow.yml)
![Coverage Status](https://github.com/jeremander/garbanzo/raw/coverage-badge/coverage-badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://raw.githubusercontent.com/jeremander/garbanzo/main/LICENSE)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

A collection of utilities related to the beancount (plaintext accounting) framework.

Eventually, some of the more public-facing utilities may be migrated to another library.

## This Repository

- `garbanzo/`: Main Python package for garbanzo
- `hooks/`: pre-commit [hooks](#pre-commit-hooks)
- `pyproject.toml`: config file for the `garbanzo` Python package, including the list of requirements
    - At present we are maintaining [forks](#forks-of-other-libraries) of some libraries which are not yet compatible with `beancount` v3. Eventually we hope to be able to use the standard versions.
- `tests/`: Contains unit test modules.
    - `tests/examples/`: Contains example files for tests, etc.

## Installing the Library

To install the `garbanzo` Python library, do `pip install .` (or `uv pip install .`) from the top-level directory.

## Command-line Program

Installing the library will also install the `garbanzo` command-line program. To see the menu of subcommands, run `garbanzo --help`.

Next we provide an overview of the different subcommands.

### `dl-assistant`

Assists in manually downloading data files from financial institutions and importing them into your beancount ledger.

**Usage**: `garbanzo dl-assistant [ACCOUNTS_FILE] [DATA_DIR]`

This command takes advantage of two metadata fields on "open" directives:

1. `url`: url to transaction download page
2. `manual_edit`: `true` or `false`

The `url` field will tell `dl-assistant` what URL to open when handling the
account. If `manual_edit` is set to `true`, `dl-assistant` won't check for
downloads, and will instead prompt to open the transaction file to add
transactions manually.

### `filter`

Applies one or more filters to entries in a beancount ledger. A *filter* is a function that can either remove entries or (more commonly) modify their contents, e.g. to impose a set of "rules" for assigning narrations/accounts in a consistent way.

**Usage**: `garbanzo filter [LEDGER_FILE] --json-filters [JSON_FILES] --inplace`

- `LEDGER_FILE` is your top-level ledger file. This may have "include" statements to incorporate multiple beancount files, in which case the tool will normalize all included files.
- `JSON_FILES` is a list of one or more paths to JSON files, each of which must contain a list of filters. See below for a description of the JSON schema for specifying filters.

It is generally preferable to use the `--inplace` flag, which will modify all of the files in-place. Otherwise, it will save copies of each file, applying a `.filt.beancount` suffix to each one.

In the future we plan to add more default filters, in addition to expanding the JSON filter schema.

#### JSON Filter Schema

You can specify custom rules for modifying transactions via the `--json-filters` argument. See [`filters.json`](tests/examples/filters.json) for an example of a JSON filter file. It should consist of a list of JSON objects, each containing two keys, `match` and `set`. Each ledger entry will be checked on each filter's `match` condition, and if it matches, the `set` condition will be triggered, possibly modifying the entry. Entries that do not match will be left alone.

At present the JSON filters only apply to transactions, not other types of beancount entries.

The current schema is described below (but note that it is subject to change):

- `match`: a JSON object with the following fields (all optional):
    - `narration` (string): [regular expression](https://docs.python.org/3/howto/regex.html#regex-howto) to match the narration
    - `payee` (string): regular expression to match the payee
    - `account_prefixes` (list of strings): account prefixes to match
        - Matches a transaction if for each prefix listed, some posting exists with that prefix.

**NOTE**: Regular expressions only need to match a part of a string, and they match case-insensitively. For example, the regular expression `PIZZA` will match the string `Vincent's Pizza`.

**NOTE**: If multiple fields are set, *all* of the criteria will have to be matched. There is currently no way to match on "any" instead of "all," but in the future there may be.

- `set`: a JSON object with the following fields (all optional):
    - `narration` (string): narration to set
    - `payee` (string): payee to set
    - `tags` (list of strings): tags to set
    - `links` (list of strings): links to set
    - `account` (string): account to set
        - Since transactions have multiple postings, this account will only be set for a unique posting matching this account type.
        - For example, if the value of `account` is `"Expenses:Food:Restaurants"`, then it will modify a posting whose account starts with `Expenses`, provided it is the only such posting.

**NOTE**: If a field's value is set to `null`, the corresponding value of the beancount entry will be removed. In contrast, if a field is absent, the value will be left alone. (In other words, absent and `null`-valued do *not* mean the same thing.)

As an illustration of the JSON filter system, if you run the `filter` subcommand on [`transactions.beancount`](tests/examples/transactions.beancount) using [`filters.json`](tests/examples/filters.json), the result is [`transactions.filtered.beancount`](tests/examples/transactions.filtered.beancount).

### `normalize`

Normalizes a beancount ledger. Sorts entries, normalizes whitespace and currency alignment.

**Usage**: `garbanzo normalize [LEDGER_FILE] --inplace`

Here `LEDGER_FILE` is your top-level ledger file. This may have "include" statements to incorporate multiple beancount files, in which case the tool will normalize all included files.

It is generally preferable to use the `--inplace` flag, which will modify all of the files in-place. Otherwise, it will save copies of each file, applying a `.norm.beancount` suffix to each one.

## Pre-commit Hooks

This repo provides [pre-commit](https://pre-commit.com/) hooks, defined in [.pre-commit-hooks.yaml](.pre-commit-hooks.yaml).

Currently there is one hook defined called `bean-check`, which you can install in your beancount ledger repository to validate the ledger before each commit.

To install it:

1. Make sure you have the `pre-commit` tool installed (e.g. with `pip install pre-commit`).
2. Create a `.pre-commit-config.yaml` file at the top level of your repository. It should be identical to the [example-pre-commit.yaml](hooks/example-pre-commit-config.yaml) file, except you should replace `"my_ledger.beancount"` with the path to your own ledger file. Then run `git add .pre-commit-config.yaml` to add it to your repo.
3. Run `pre-commit install`.

The hook should now be installed in `.git/hooks/pre-commit`. It will run automatically whenever you make a commit (as long as at least one file has been updated). You can also do `pre-commit run` to run the hook without having to commit.

## Links

- [beancount](https://github.com/beancount/beancount): core library
    - Main [documentation](https://beancount.github.io/docs/)
    - Current version is [v3](https://beancount.github.io/docs/beancount_v3.html), still transitioning from v2.
- [fava](https://github.com/beancount/fava): web front-end
- [BeanHub](https://beanhub.io): enterprise-grade app built on beancount
    - Free tier only allows 1,000 entries in personal repo.
- [lazy-beancount](https://github.com/Evernight/lazy-beancount): batteries-included system (web interface, extra plugins)
- [beancount-lazy-plugins](https://github.com/Evernight/beancount-lazy-plugins): plugins for beancount, most notably:
    - `valuation`: track total value of the opaque fund over time
    - `filter_map`: apply operations to group of transactions selected by Fava filters

### Auto-importing

- [SimpleFin](https://www.simplefin.org): open-source interchange language for financial transactions
- [Plaid](https://plaid.com): popular enterprise financial API
- [beanhub-import](/blog/2024/05/27/introduction-of-beanhub-import/): one small step closer to fully automating transaction importing ([Github repo](https://github.com/LaunchPlatform/beanhub-import))

### Forks of other libraries

- [beancount-import](https://github.com/jeremander/beancount-import): Import entries from raw data files.
    - [v3-compat](https://github.com/jeremander/beancount-import/tree/v3-compat) branch
- [beangulp](https://github.com/jeremander/beangulp): New importer framework
    - [v3-fixups](https://github.com/jeremander/beangulp/tree/v3-fixups) branch
