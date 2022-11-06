"""Logging module."""

import logging

import click
import emoji
from rich.logging import RichHandler
from rich.traceback import install

EXCLUDED_LOGGERS = (
    "numba",
    "matplotlib",
    "connectionpool",
    "docker.auth",
    "docker.utils.config",
    "requests.packages.urllib3",
    "requests",
    "urllib3.connectionpool",
    "docker.api.build",
    "black",
    "blackd",
    "blib2to3",
)


class RichEmojiFilteredHandler(RichHandler):
    """Extended rich handler with emoji filter support."""

    def __init__(self, *args, enable_emoji=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.enable_emoji = enable_emoji

    def format(self, record: logging.LogRecord) -> str:
        """Extends RichHandler. Format to filter out emoji."""
        formatted = super().format(record)
        formatted = (
            formatted
            if self.enable_emoji
            else emoji.replace_emoji(formatted).strip()
        )
        return formatted


def init(verbose: bool = False, enable_emoji=False, rich=True) -> None:
    """
    Init logging.
        Args:
            verbose (bool):
                Verbose level (DEBUG) or not (INFO).
            enable_emoji (bool):
                Enable emoji in logs or not.
            rich (bool):
                Enable rich handler & traceback or not.
        Raises:
            AnyError: If anything bad happens.
    """

    for log_name in EXCLUDED_LOGGERS:
        other_log = logging.getLogger(log_name)
        other_log.setLevel(logging.WARNING)

    if enable_emoji:
        assert rich, "Emoji can be enabled only with rich handler"

    if not rich:
        logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)
        return

    logging.basicConfig(
        level="DEBUG" if verbose else "INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichEmojiFilteredHandler(
                rich_tracebacks=True,
                markup=True,
                enable_link_path=False,
                enable_emoji=enable_emoji,
            )
        ],
    )

    install(suppress=[click])
