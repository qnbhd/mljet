"""Dispatcher for supported model types."""
import importlib.util
import logging
import sys
from functools import lru_cache
from pathlib import Path
from types import ModuleType
from typing import (
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
)

from deployme.contrib.supported import ModelType

BASES_PATH = Path(__file__).parent.resolve()

log = logging.getLogger(__name__)


@lru_cache(None)
def get_all_supported_ml_kinds() -> Dict[str, ModuleType]:
    """Returns all default backends."""
    supported2mod = {}

    for x in filter(
        lambda y: (
            y.is_file()
            and not y.name.startswith("__")
            and y.name != Path(__file__).name
        ),
        BASES_PATH.rglob("*.py"),
    ):
        spec = importlib.util.spec_from_file_location(x.stem, x)
        if not spec:
            continue
        mod = importlib.util.module_from_spec(spec)
        sys.modules[x.stem] = mod
        spec.loader.exec_module(mod)  # type: ignore
        used_for = getattr(mod, "USED_FOR", [])
        if not used_for:
            log.critical(
                f"Module {x.stem} exists but has no `USED_FOR`, skipping"
            )
        for mt in used_for:
            supported2mod[mt] = mod
    return supported2mod


SUPPORTED_ML_KINDS = get_all_supported_ml_kinds()


def get_dual_methods(mt: ModelType, methods: Sequence[str]) -> List[Callable]:
    """Get dual methods, needed to replace in backend templates."""
    mod = SUPPORTED_ML_KINDS.get(mt)
    if not mod:
        raise ValueError(f"No such model type: {mt}")
    dual: List[Callable] = []
    for method in methods:
        w: Optional[Callable] = getattr(mod, method, None)
        if w is None:
            raise ValueError(f"Method `{method}` not supported for {mt}")
        dual.append(w)
    return dual
