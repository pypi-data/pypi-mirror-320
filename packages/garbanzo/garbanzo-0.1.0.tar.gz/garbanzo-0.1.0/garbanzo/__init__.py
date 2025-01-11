import logging

from rich.console import Console
from rich.logging import RichHandler


__version__ = '0.1.0'

PROG = 'garbanzo'

LOG_FMT = '%(message)s'

# create global logger

console = Console(stderr=True)

handler = RichHandler(
    show_time=False,
    show_level=True,
    show_path=False,
    markup=True,
    console=console,
)

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FMT,
    handlers=[handler],
)

logger = logging.getLogger(PROG)
