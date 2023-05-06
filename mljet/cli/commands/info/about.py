"""CLI about command module."""
# flake8: noqa

import click
from rich.console import Console

console = Console()


@click.command("about")
def about():
    """Show the MLJET information."""
    console.print(  # noqa: W293, W291
        r"""[white on #8B43EE]
                                                                         
  ██████╗ ███████╗██████╗ ██╗      ██████╗ ██╗   ██╗███╗   ███╗███████╗  
  ██╔══██╗██╔════╝██╔══██╗██║     ██╔═══██╗╚██╗ ██╔╝████╗ ████║██╔════╝  
  ██║  ██║█████╗  ██████╔╝██║     ██║   ██║ ╚████╔╝ ██╔████╔██║█████╗    
  ██║  ██║██╔══╝  ██╔═══╝ ██║     ██║   ██║  ╚██╔╝  ██║╚██╔╝██║██╔══╝    
  ██████╔╝███████╗██║     ███████╗╚██████╔╝   ██║   ██║ ╚═╝ ██║███████╗  
  ╚═════╝ ╚══════╝╚═╝     ╚══════╝ ╚═════╝    ╚═╝   ╚═╝     ╚═╝╚══════╝  
                                                                         [/]

MLJET - minimalistic ML-models auto mljetnt tool.

Authors:
    - Templin Konstantin <1qnbhd@gmail.com>
    - Kristina Zheltova <masterkristall@gmail.com>

Github: https://github.com/qnbhd/mljet
PyPI: https://pypi.org/project/mljet/
ReadTheDocs: https://mljet.readthedocs.io/en/latest/
"""
    )
