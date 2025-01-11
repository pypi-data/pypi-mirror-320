from dataclasses import dataclass, field
import datetime
import os
from pathlib import Path
import subprocess
import webbrowser

from beancount.core.data import Account
from fancy_dataclass import CLIDataclass
import rich
from rich.markdown import Markdown
from rich.prompt import InvalidResponse, Prompt, PromptBase
from rich.text import Text

from garbanzo import logger
from garbanzo.helpers import get_relative_account_dir, string_is_date
from garbanzo.ledger import BeancountLedger


class SkipAccountError(Exception):
    """Exception raised to skip an account."""

    pass


class ConfirmWithSkip(PromptBase[bool]):
    """Rich prompt that acts similarly to 'Confirm' but adds a third option to skip
    an account by raising an exception.
    """

    response_type = bool
    validate_error_message = '[prompt.invalid]Please enter Y, N, or S to skip this account'
    choices: list[str] = ['y', 'n', 's']

    def render_default(self, default: bool) -> Text:  # type: ignore[override]
        """Render the default as (y) or (n) rather than True/False."""
        yes, no, _ = self.choices
        return Text(f'({yes})' if default else f'({no})', style='prompt.default')

    def process_response(self, value: str) -> bool:
        """Convert choices to a bool."""
        value = value.strip().lower()
        if value not in self.choices:
            raise InvalidResponse(self.validate_error_message)
        if value == self.choices[-1]:
            raise SkipAccountError()
        return value == self.choices[0]


@dataclass
class AccountMetadata:
    """Account metadata relevant to the download helper."""

    account: Account
    url: str | None = None
    manual_edit: bool = False


def _edit_file(filepath: Path) -> None:
    """Open the given file in the user's default $EDITOR.
    Wait for the editor to close before resuming execution.

    :param filepath: Path to the file to be edited.
    """
    editor = os.environ.get('EDITOR', 'nano')

    try:
        subprocess.run([editor, str(filepath)], check=True)
    except FileNotFoundError:
        logger.error(f'Editor {editor!r} not found')
    except Exception as e:
        logger.error(str(e))


def _add_date_prefix_to_file_name(file_name: str) -> str:
    if len(file_name) > 10 and string_is_date(file_name[:10]):
        return file_name

    today_date = datetime.datetime.now().strftime('%Y-%m-%d')
    return f'{today_date}-{file_name}'


def _move_and_rename_files(files: list[Path], dir_path: Path) -> None:
    for filepath in files:
        new_name = dir_path / _add_date_prefix_to_file_name(filepath.name)
        dir_path.mkdir(parents=True, exist_ok=True)
        filepath.rename(new_name)
        rich.print(f'{filepath.name} -> {new_name.name}')


def _find_recent_files(directory: Path, since_datetime: datetime.datetime) -> list[Path]:
    directory_path = Path(directory)
    recent_files = []

    for file_path in directory_path.iterdir():
        if not file_path.is_file():
            continue
        if file_path.name.startswith('.'):
            continue
        creation_time = datetime.datetime.fromtimestamp(file_path.stat().st_ctime)
        if creation_time > since_datetime:
            recent_files.append(file_path)

    return recent_files


def _handle_account(account: AccountMetadata, download_dir: Path, data_dir: Path, transactions_file: Path | None) -> None:
    if not account.url:
        return

    rich.print(f"[bold cyan]Handling:[/] [bold blue]{account.account}[/] [grey](Press 's' at any point to skip)[/]")
    resp = ConfirmWithSkip.ask(f'[bold cyan]Open:[/] [bold]{account.url}[/]', default=True)
    if resp:
        webbrowser.open(account.url)

    cur_time = datetime.datetime.now()
    new_downloads = []
    if not account.manual_edit:
        Prompt.ask('[bold cyan]Waiting for download...[/] (press Enter when file(s) downloaded)')
        new_downloads = _find_recent_files(directory=download_dir, since_datetime=cur_time)
    if account.manual_edit or not new_downloads:
        prompt_str = 'Account marked as manual entry, go to transactions file now?'
        if not account.manual_edit:
            prompt_str = '[yellow]Found no downloaded files.[/] Edit transactions manually instead?'
        resp = ConfirmWithSkip.ask(
            prompt_str,
            default=account.manual_edit,
        )
        if resp:
            if not transactions_file:
                rich.print('[red]No transactions file given[/]')
            else:
                _edit_file(transactions_file)
        return

    files = '\n'.join([f'- {f.name}' for f in new_downloads])
    rich.print('[bold cyan]Found downloaded files:[/]')
    rich.print(Markdown(files))

    directory = data_dir / get_relative_account_dir(account.account)
    resp = ConfirmWithSkip.ask(f'Move file(s) to [bold green]{directory}[/]?', default=True)
    if resp:
        _move_and_rename_files(files=new_downloads, dir_path=directory)

    rich.print('[bold magenta]----------[/]')


def _load_accounts_from_file(accounts_file: Path) -> list[AccountMetadata]:
    ledger = BeancountLedger.load_file(accounts_file)
    metas = []
    for entry in ledger.open_directives:
        is_manual_edit = entry.meta.get('manual_edit', 'false').lower().strip() == 'true'
        metas.append(AccountMetadata(account=entry.account, url=entry.meta.get('url'), manual_edit=is_manual_edit))
    return metas


def download_assistant(accounts_file: Path, data_dir: Path, download_dir: Path | None = None, transactions_file: Path | None = None) -> None:
    """Entrypoint for the download assistant. Given a set of accounts with a
    'url' metadata tag, will guide the user through downloading data for each
    account. When data is downloaded, automatically tags it with a date (so that
    it is picked up by the fava "documents" tab) and moves it into the proper
    directory.
    """
    if not data_dir.exists():
        raise RuntimeError(f'Data directory not found: {data_dir!r}')

    if not download_dir:
        download_dir = Path.home() / 'Downloads'

    for account in _load_accounts_from_file(accounts_file=accounts_file):
        try:
            _handle_account(account=account, data_dir=data_dir, download_dir=download_dir, transactions_file=transactions_file)
        except SkipAccountError:
            rich.print(f'\n[bold yellow]Skipping account:[/] {account.account}\n')
            continue


@dataclass
class DownloadAssistantCmd(CLIDataclass, command_name='dl-assistant'):
    """Download assistant for beancount accounts."""

    accounts_file: Path = field(metadata={'help': 'input file containing accounts'})
    data_dir: Path = field(metadata={'help': 'path to directory where downloads should be moved'})
    download_dir: Path | None = field(default=None, metadata={'help': 'directory where downloads are looked for'})
    transactions_file: Path | None = field(default=None, metadata={'help': 'file to which transactions are written'})

    def run(self) -> None:
        download_assistant(accounts_file=self.accounts_file, data_dir=self.data_dir, download_dir=self.download_dir, transactions_file=self.transactions_file)
