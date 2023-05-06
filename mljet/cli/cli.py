"""Module that contains autodiscovery mechanism for click CLI interface"""
import importlib.util
import sys
from pathlib import Path

import click


class Cli(click.MultiCommand):
    """
    Autodiscovery mechanism for click CLI interface (MultiCommand)
    Scan `COMMANDS_FOLDER` for all python files and import them as commands.

    Spec:
        - All python files in `COMMANDS_FOLDER` are considered as commands
        - In each file there should be a function with the same name as a file,
          this function will be used as a command.

    Args:
        commands_folder: Path to the folder with commands.
    """

    def __init__(self, commands_folder):
        super(Cli, self).__init__(
            name="mljet", help="Minimalistic ML models mljetnt tool."
        )

        self.cmd2path = {}

        for script_path in filter(
            lambda x: not str(x.name).startswith("_"),
            Path(commands_folder).rglob("*.py"),
        ):
            sys.path.append(script_path.name)
            self.cmd2path[script_path.stem.replace("_", "-")] = script_path

    def list_commands(self, ctx):
        cmds = list(self.cmd2path.keys())
        return sorted(cmds)

    def get_command(self, ctx, name):
        path = self.cmd2path.get(name)
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, name.replace("-", "_"))


COMMANDS_FOLDER = Path(__file__).parent.joinpath("commands")
cli = Cli(COMMANDS_FOLDER)


if __name__ == "__main__":
    cli()
