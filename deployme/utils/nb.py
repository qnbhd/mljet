"""Module that contains the code for handling Jupyter notebooks."""

from typing import (
    List,
    Literal,
    TypedDict,
)

from nbformat import read

from deployme.utils.types import PathLike

__all__ = ["get_code_from_ipynb", "get_code_cells_sources_from_notebook"]


class _Cell(TypedDict):
    """
    A cell in a Jupyter notebook.

    Attributes:
        cell_type: The type of cell.
        source: The source code of the cell.
    """

    cell_type: Literal["code", "markdown", "raw"]
    source: str


class _Notebook(TypedDict):
    """
    A Jupyter notebook.

    Attributes:
        cells: The cells in the notebook.
    """

    cells: List[_Cell]
    nbformat: int
    nbformat_minor: int


def get_code_cells_sources_from_notebook(notebook: _Notebook) -> List[str]:
    """
    Get the source code of all code cells in a notebook.

    Args:
        notebook: The notebook to get the code cells from.

    Returns:
        The source code from the code cells in the notebook.
    """

    return [
        cell["source"]
        for cell in notebook["cells"]
        if cell["cell_type"] == "code" and cell["source"].strip()
    ]


def get_code_from_ipynb(path: PathLike, explicit_version: int = 4) -> List[str]:
    """
    Get the source code from a Jupyter notebook.

    Args:
        path: The path to the notebook.

    Returns:
        The source code from the notebook.

    Raises:
        FileNotFoundError: If the notebook does not exist.
        :class:`nbformat.reader.NotJSONError`: If the notebook is not valid JSON.
        :class:`jsonschema.exceptions.ValidationError`: If validation fails.
        :class:`nbformat.NBFormatError`: If the notebook has an invalid version.

    .. note::
        The notebook version will be explicitly
        converted to version ``explicit_version``.

    """

    with open(path) as f:
        notebook = read(f, explicit_version)

    return get_code_cells_sources_from_notebook(notebook)
