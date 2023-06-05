"""Utils module."""
import inspect
import re
from typing import Callable

CLS_REGEX = re.compile(
    r"<class\s'(.*?)'>", re.IGNORECASE | re.MULTILINE | re.DOTALL
)


def drop_unnecessary_kwargs(func: Callable, kwargs: dict) -> dict:
    """Drop unnecessary kwargs."""
    spec = inspect.getfullargspec(func).args
    return {
        param: param_value
        for param, param_value in kwargs.items()
        if param in spec
    }


def is_package_installed(name: str) -> bool:
    """Check if package is installed and valid."""
    try:
        __import__(name)
        return True
    except Exception:
        return False


def parse_cls_name(obj) -> str:
    """Parse class name."""
    match_obj = CLS_REGEX.match(str(type(obj)))
    if match_obj:
        return match_obj.group(1)
    return str(type(obj))
