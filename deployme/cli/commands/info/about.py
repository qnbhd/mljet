"""CLI about command module."""
# flake8: noqa

import click
from rich.console import Console

console = Console()


@click.command("about")
def about():
    """Show the DeployMe information."""
    console.print(  # noqa: W293, W291
        r"""[white on #8B43EE]
                                                                         
  ██████╗ ███████╗██████╗ ██╗      ██████╗ ██╗   ██╗███╗   ███╗███████╗  
  ██╔══██╗██╔════╝██╔══██╗██║     ██╔═══██╗╚██╗ ██╔╝████╗ ████║██╔════╝  
  ██║  ██║█████╗  ██████╔╝██║     ██║   ██║ ╚████╔╝ ██╔████╔██║█████╗    
  ██║  ██║██╔══╝  ██╔═══╝ ██║     ██║   ██║  ╚██╔╝  ██║╚██╔╝██║██╔══╝    
  ██████╔╝███████╗██║     ███████╗╚██████╔╝   ██║   ██║ ╚═╝ ██║███████╗  
  ╚═════╝ ╚══════╝╚═╝     ╚══════╝ ╚═════╝    ╚═╝   ╚═╝     ╚═╝╚══════╝  
                                                                         [/]

DeployMe - minimalistic ML-models auto deployment tool.

Authors:
    - Templin Konstantin <1qnbhd@gmail.com>
    - Kristina Zheltova <masterkristall@gmail.com>

Github: https://github.com/qnbhd/deployme
PyPI: https://pypi.org/project/deployme/
ReadTheDocs: https://deployme.readthedocs.io/en/latest/
"""
    )
