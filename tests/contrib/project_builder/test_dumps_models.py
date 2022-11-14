import pickle
from pathlib import Path

import dill
import joblib
import pytest
from hypothesis import (
    given,
    strategies as st,
)

from deployme.contrib.project_builder import dumps_models
from tests.iomock import DefaultIOMock


@given(path=st.sampled_from(["project"]))
def test_dumps_models_correct_default(path):
    """Test dumps_models."""
    mocker = DefaultIOMock()
    with mocker:
        Path(path).mkdir(parents=True, exist_ok=True)
        dumps_models(path, [list(), dict()], ["model1", "model2"])
    assert (
        mocker.fs_tree
        == """|
└── models
|    ├── model1.pkl
|    ├── model2.pkl
"""
    )


@given(serializer=st.sampled_from([pickle, joblib, dill]))
def test_dumps_models_correct_custom_serializer(serializer):
    """Test dumps_models."""
    mocker = DefaultIOMock()
    with mocker:
        Path("models").mkdir(parents=True, exist_ok=True)
        dumps_models(
            "models",
            [[1, 2, 3], dict()],
            ["model1", "model2"],
            serializer=serializer,
            ext="compressed",
        )
    assert (
        mocker.fs_tree
        == """|
└── models
|    ├── model1.compressed
|    ├── model2.compressed
"""
    )


@given(path=st.from_regex(r"[\w\d_-]+", fullmatch=True))
def test_dumps_models_path_mismatched_length(path):
    """Test dumps_models."""
    mocker = DefaultIOMock()
    with mocker:
        Path(path).mkdir(parents=True, exist_ok=True)
        with pytest.raises(ValueError):
            dumps_models(path, [list(), dict()], ["model1", "model2", "model3"])
