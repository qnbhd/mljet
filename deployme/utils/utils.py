"""Utils module."""
import inspect
from typing import Callable


def drop_unnecessary_kwargs(func: Callable, kwargs: dict) -> dict:
    """Drop unnecessary kwargs."""
    spec = inspect.getfullargspec(func).args
    return {
        param: param_value
        for param, param_value in kwargs.items()
        if param in spec
    }


def is_package_installed(name: str) -> bool:
    """Check if package is installed."""
    try:
        __import__(name)
        return True
    except ImportError:
        return False
