"""CLI version command module."""

import click

from mljet import __version__
from mljet.cli.helpers import (
    appearance,
    format_info,
)


@click.command("version")
@appearance(dest_printer="echo", dest_formatting="formatting")
def version(echo, formatting):
    """Show the MLJET version information."""
    echo(format_info("version", __version__, formatting))
