"""CLI strategies-list command module."""

import click

from deployme.cli.helpers import (
    appearance,
    format_info,
)
from deployme.contrib.supported import Strategy


@click.command("strategies-list")
@appearance(dest_printer="echo", dest_formatting="formatting")
def strategies_list(echo, formatting):
    """Prints supported strategies."""
    supported = [s.replace("Strategy.", "") for s in Strategy]
    echo(format_info("strategy", supported, formatting))
