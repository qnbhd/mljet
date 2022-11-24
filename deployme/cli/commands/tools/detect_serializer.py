"""CLI detect-serializer command module."""

import click

from deployme.cli.helpers import (
    appearance,
    format_info,
)
from deployme.utils.serializers import detect_model_serializer


@click.command("detect-serializer")
@click.argument(
    "path",
    type=click.Path(exists=True),
    required=True,
)
@appearance(dest_printer="echo", dest_formatting="formatting")
def detect_serializer(path, echo, formatting):
    """Detects the serializer of the model."""
    serializer = detect_model_serializer(path)
    echo(format_info("serializer", serializer, formatting))
