"""CLI helpers module."""

import json
from typing import (
    Literal,
    Optional,
    Union,
)

import click
import pandas as pd
from click import option
from rich.console import Console

from mljet.utils.funcs import (
    compose,
    identity,
)

console = Console()


class Printer(click.ParamType):
    name = "printer"

    def convert(self, value, param, ctx):
        if value == "colorized":
            return console.print
        if value == "no-color":
            return click.echo
        raise click.BadParameter("Unknown printer")


# Colorization

_colorized_option = lambda dest: option(
    "--colorized",
    dest,
    flag_value="colorized",
    type=Printer(),
    help="Colorizes the output.",
)
_no_color_option = lambda dest: option(
    "--no-color",
    dest,
    flag_value="no-color",
    default=True,
    type=Printer(),
    help="Prints the output without colorization.",
)

# Formatting

_plain_option = lambda dest: option(
    "--plain",
    dest,
    default=True,
    flag_value="plain",
    help="Prints the output without any formatting.",
)
_markdown_option = lambda dest: option(
    "--markdown", dest, flag_value="markdown", help="Prints in Markdown format."
)
_json_option = lambda dest: option(
    "--json", dest, flag_value="json", help="Prints in JSON format."
)


def appearance(
    *, dest_printer: Optional[str] = None, dest_formatting: Optional[str] = None
):
    """
    Decorator for appearance options.

    Args:
        dest_printer: The argument name for the printer.
        dest_formatting: The argument name for the formatting.

    Returns:
        Appearance options.
    """

    deco = identity
    if dest_printer is not None:
        deco = compose(
            _colorized_option(dest_printer),
            _no_color_option(dest_printer),
            deco,
        )
    if dest_formatting is not None:
        deco = compose(
            _markdown_option(dest_formatting),
            _json_option(dest_formatting),
            _plain_option(dest_formatting),
            deco,
        )
    return deco


Jsonable = Union[dict, list, str, int, float, bool, None]
Format = Literal["markdown", "json", "plain"]


def _plain_formatter(data: Jsonable) -> str:
    if isinstance(data, list):
        return ",".join(map(str, data))
    if isinstance(data, str):
        return data
    return json.dumps(data)


def format_info(name: str, data: Jsonable, fmt: Format) -> str:
    """
    Formats the info.

    Args:
        name: The name of the info.
        data: Data to format.
        fmt: The format to use.

    Returns:
        Formatted info.
    """

    if fmt == "markdown":
        if isinstance(data, (int, float, str, bool)) or data is None:
            data = [data]
        return pd.Series(data, name=name).to_markdown()
    if fmt == "json":
        return json.dumps({name: data}, indent=4)
    return _plain_formatter(data)
