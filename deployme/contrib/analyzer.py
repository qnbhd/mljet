"""Models analyzed and method's extractor."""

import inspect
import warnings
from typing import (
    Callable,
    Dict,
)

from deployme.contrib.supported import ModelType
from deployme.cookie.templates.ml.dispatcher import get_dual_methods

_SUPPORTED_METHODS = (
    "predict",
    "predict_proba",
)


def extract_methods_names(model):
    """Get methods from model."""
    return [
        x[0]
        for x in inspect.getmembers(model, inspect.ismethod)
        if not x[0].startswith("_")
        and x[0].startswith("predict")
        and x[0] in _SUPPORTED_METHODS
    ]


def get_methods_names_and_associated_wrappers(
    model,
) -> Dict[str, Callable]:
    """Get methods names and associated wrappers."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        extracted = extract_methods_names(model)
    mt = ModelType.from_model(model)
    return dict(zip(extracted, get_dual_methods(mt, extracted)))
