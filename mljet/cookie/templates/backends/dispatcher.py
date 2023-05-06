"""Dispatch for default backends."""

from functools import lru_cache
from pathlib import Path
from typing import (
    Dict,
    Optional,
)

BASES_PATH = Path(__file__).parent


@lru_cache(None)
def get_all_default_backends() -> Dict[str, Path]:
    """Returns all default backends."""
    return {
        x.stem.replace("_", ""): x
        for x in BASES_PATH.iterdir()
        if x.is_dir() and not x.name.startswith("__")
    }


SUPPORTED_BACKENDS = get_all_default_backends()


def dispatch_default_backend(backend_name, strict=False) -> Optional[Path]:
    """Dispatches default backend by name."""
    backends = get_all_default_backends()
    backend = backends.get(backend_name)
    if backend is None and strict:
        raise ValueError(f"Backend `{backend_name}` is not found")
    return backend
