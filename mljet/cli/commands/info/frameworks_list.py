"""CLI framework-list command module."""

import click

from mljet.cli.helpers import (
    appearance,
    format_info,
)
from mljet.contrib.supported import ModelType


@click.command("frameworks-list")
@appearance(dest_printer="echo", dest_formatting="formatting")
def frameworks_list(echo, formatting):
    """Display the list of supported ML frameworks models"""
    supported = [m.replace("ModelType.", "") for m in ModelType]
    echo(format_info("framework", supported, formatting))
