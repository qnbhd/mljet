"""Models analyzed and method's extractor."""

import inspect
import json
import logging
import warnings
from typing import (
    Callable,
    Dict,
    List,
)

from deployme.contrib.supported import ModelType
from deployme.cookie.templates.ml.dispatcher import get_dual_methods
from deployme.utils.types import Estimator

_SUPPORTED_METHODS = (
    "predict",
    "predict_proba",
)

log = logging.getLogger(__name__)


def extract_methods_names(model: Estimator) -> List[str]:
    """Get methods from model."""
    return [
        member[0]
        for member in inspect.getmembers(model, inspect.ismethod)
        if not member[0].startswith("_")
        and member[0].startswith("predict")
        and member[0] in _SUPPORTED_METHODS
    ]


def get_associated_methods_wrappers(
    model: Estimator,
) -> Dict[str, Callable]:
    """Get methods names and associated wrappers."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        extracted = extract_methods_names(model)
    mt = ModelType.from_model(model)
    associated = dict(zip(extracted, get_dual_methods(mt, extracted)))
    log.info(f"Detected model methods: {json.dumps(extracted, indent=4)}")
    return associated
