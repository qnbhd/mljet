from pathlib import Path

import pytest
from hypothesis import (
    given,
    strategies as st,
)

from deployme.contrib.project_builder import init_project_directory
from tests.iomock import DefaultIOMock


@given(path=st.from_regex(r"[\w\d_-]+", fullmatch=True))
def test_init_project_directory_correct(path):
    """Test init_project_directory."""
    mocker = DefaultIOMock()
    with mocker:
        init_project_directory(path)
    assert (
        mocker.fs_tree
        == f"""|
└── {path}
|    ├── data
|    ├── models
"""
    )


@given(path=st.from_regex(r"[\w\d_-]+", fullmatch=True))
def test_init_project_directory_path_is_exists(path):
    """Test init_project_directory."""
    mocker = DefaultIOMock()
    with mocker:
        Path(path).mkdir(parents=True, exist_ok=True)
        with pytest.raises(FileExistsError):
            init_project_directory(path)


@given(path=st.from_regex(r"[\w\d_-]+", fullmatch=True))
def test_init_project_directory_path_is_file_force(path):
    """Test init_project_directory."""
    mocker = DefaultIOMock()
    with mocker:
        Path(path).mkdir(parents=True, exist_ok=True)
        init_project_directory(path, force=True)
    assert (
        mocker.fs_tree
        == f"""|
└── {path}
|    ├── data
|    ├── models
"""
    )
