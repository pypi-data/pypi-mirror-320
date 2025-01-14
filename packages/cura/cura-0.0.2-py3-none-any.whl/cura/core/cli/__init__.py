import logging
from dataclasses import dataclass
from typing import Optional, Annotated

import structlog
import typer
from rich.console import Console
from rich.logging import RichHandler

from ..util import sync

logger = structlog.get_logger()

app = typer.Typer()


@dataclass(kw_only=True)
class GlobalOptions:
    """Global options that apply to all commands, before the command verb."""


options: Optional[GlobalOptions] = None


@app.callback()
def callback(
        log_level: Annotated[str, typer.Option(
            metavar='NAME',
            help="""logging level, e.g. debug, info, warning, error""",
        )] = 'warning',
):
    global options
    options = GlobalOptions()
    logging.getLogger().setLevel(log_level.upper())
    logger.debug("initialized global options", options=options)


@app.command()
@sync
async def version():
    """Print the version."""
    from .. import __version__
    print(f'cura {__version__}')


def main():
    logging.basicConfig(format="%(message)s", datefmt="[%X]",
                        handlers=[RichHandler(rich_tracebacks=True,
                                              console=Console(stderr=True))])
    structlog.configure(processors=[
        structlog.stdlib.filter_by_level,
        # structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ], logger_factory=structlog.stdlib.LoggerFactory())
    return app()