#!/usr/bin/env python3

from argparse import RawTextHelpFormatter
from dataclasses import dataclass, field
import sys
from typing import Optional, Union

from fancy_dataclass import CLIDataclass

from garbanzo import __version__, logger
from garbanzo.cli.download_assistant import DownloadAssistantCmd
from garbanzo.cli.filter import FilterCmd
from garbanzo.cli.normalize import NormalizeCmd


@dataclass
class GarbanzoCLI(CLIDataclass, version=f'%(prog)s {__version__}', formatter_class=RawTextHelpFormatter):
    """Assorted utilities for interacting with a beancount ledger."""

    subcommand: Union[
        DownloadAssistantCmd,
        FilterCmd,
        NormalizeCmd,
    ] = field(metadata={'subcommand': True})

    @classmethod
    def main(cls, arg_list: Optional[list[str]] = None) -> None:
        """Add custom error handling to main function to exit gracefully when possible."""
        try:
            super().main(arg_list=arg_list)  # delegate to subcommand
        except Exception as e:
            logger.error(str(e))
            sys.exit(1)


if __name__ == '__main__':
    GarbanzoCLI.main()
