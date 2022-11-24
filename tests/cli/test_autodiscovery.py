from pathlib import Path

import pytest
from click.testing import CliRunner

from deployme.cli.cli import cli

commands_path = Path(__file__).parent.parent.parent.joinpath(
    "deployme", "cli", "commands"
)
commands = tuple(
    (
        cmd.stem.replace("_", "-")
        for cmd in filter(
            lambda x: not str(x.name).startswith("_"),
            commands_path.rglob("*.py"),
        )
    )
)
runner = CliRunner()
result = runner.invoke(cli, ["--help"])


@pytest.mark.parametrize("command", commands)
def test_autodiscovery(command):
    assert command in result.output
