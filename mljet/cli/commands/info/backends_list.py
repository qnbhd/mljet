"""CLI backend-list command module."""

import click

from mljet.cli.helpers import (
    appearance,
    format_info,
)
from mljet.cookie.templates.backends.dispatcher import SUPPORTED_BACKENDS


@click.command("backends-list")
@appearance(dest_printer="echo", dest_formatting="formatting")
def backends_list(echo, formatting):
    """List supported backends."""
    supported = list(SUPPORTED_BACKENDS.keys())
    echo(format_info("backend", supported, formatting))
