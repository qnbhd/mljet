"""Dispatcher for supported model types."""

from typing import (
    Callable,
    Sequence,
)

from deployme.contrib.supported import ModelType
from deployme.cookie.templates.ml import _sklearn


def get_dual_methods(
    mt: ModelType, methods: Sequence[str]
) -> Sequence[Callable]:
    """Get dual methods, needed to replace in backend templates."""
    if mt in (ModelType.SKLEARN_MODEL, ModelType.SKLEARN_PIPE):
        return [getattr(_sklearn, method) for method in methods]
    raise NotImplementedError(f"Model type {mt} is not supported")
