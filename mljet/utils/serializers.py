import pickle
from typing import Literal

import dill
import joblib
from returns.converters import flatten
from returns.result import (
    Success,
    safe,
)

from mljet.utils.types import PathLike

UnknownSerializer = "unknown"
SerializerType = Literal["pickle", "dill", "joblib", "unknown"]


def _serializer_load(serializer, stream):
    """Helper function for detecting model serializer."""
    serializer.load(stream)
    return serializer.__name__


_safe_serializer_load = safe(_serializer_load)


def detect_model_serializer(path: PathLike) -> SerializerType:
    """
    Detects model serializer.

    Args:
        path: Path to the model.

    Returns:
        Serializer type (pickle, dill, joblib),
        or "unknown" if serializer is not detected.
    """

    with open(path, "rb") as stream:
        serializer = flatten(
            _safe_serializer_load(pickle, stream)
            .lash(lambda x: _safe_serializer_load(dill, stream))
            .lash(lambda x: _safe_serializer_load(joblib, stream))
            .lash(lambda x: Success("unknown"))
        )
    return serializer
