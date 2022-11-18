from pathlib import Path

import jsonschema
import nbformat
import pytest
from hypothesis import given
from hypothesis_jsonschema import from_schema

from deployme.utils.nb import (
    _Notebook,
    get_code_cells_sources_from_notebook,
    get_code_from_ipynb,
)

NOTEBOOKS_EXAMPLES_FOLDER = Path(__file__).parent.joinpath("notebooks-examples")


@given(
    notebook=from_schema(
        {
            "type": "object",
            "required": ["cells", "nbformat", "nbformat_minor"],
            "properties": {
                "cells": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["cell_type", "source"],
                        "properties": {
                            "cell_type": {
                                "type": "string",
                                "enum": ["code", "markdown", "raw"],
                            },
                            "source": {"type": "string"},
                        },
                    },
                },
                "nbformat": {"type": "integer", "minimum": 3, "maximum": 4},
                "nbformat_minor": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 5,
                },
            },
        }
    )
)
def test_get_code_cells_sources_from_notebook(notebook: _Notebook):
    count_of_code_cells = len(
        [
            cell
            for cell in notebook["cells"]
            if cell["cell_type"] == "code" and cell["source"].strip()
        ]
    )
    sources = get_code_cells_sources_from_notebook(notebook)
    assert len(sources) == count_of_code_cells


def test_correct_notebook():
    path = NOTEBOOKS_EXAMPLES_FOLDER.joinpath("correct_notebook.ipynb")
    sources = get_code_from_ipynb(path)
    assert sources == ["import numpy", "import sklearn", "import plotly"]


def test_not_json():
    path = NOTEBOOKS_EXAMPLES_FOLDER.joinpath("not_json.ipynb")
    with pytest.raises(nbformat.reader.NotJSONError):
        get_code_from_ipynb(path)


def test_not_notebook():
    path = NOTEBOOKS_EXAMPLES_FOLDER.joinpath("not_notebook.ipynb")
    with pytest.raises(jsonschema.exceptions.ValidationError):
        get_code_from_ipynb(path)


def test_not_correct_version():
    path = NOTEBOOKS_EXAMPLES_FOLDER.joinpath("not_correct_version.ipynb")
    with pytest.raises(nbformat.NBFormatError):
        get_code_from_ipynb(path)
