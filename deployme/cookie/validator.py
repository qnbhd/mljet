"""Static code analysis of the template."""

import re
from functools import lru_cache
from typing import (
    Dict,
    List,
    Sequence,
)

from returns.iterables import Fold
from returns.pipeline import is_successful
from returns.result import (
    Success,
    safe,
)

_ENTRYPOINT_TEMPLATE = re.compile(
    r"^if\s+__name__\s+==\s+(\"__main__\"|'__main__'):$", re.MULTILINE
)
_FUN_TEMPLATE = re.compile(
    r"(async def|def)\s+([a-zA-Z_]\w*)\s*\(([^)]*)\)\s*[->]*.*:",
    re.MULTILINE,
)

__all__ = [
    "validate",
    "ValidationError",
]


class ValidationError(Exception):
    """Exception raised when the template is not valid."""


@lru_cache(maxsize=None)
def _parse_defs(source: str) -> Dict[str, List[str]]:
    """
    Parse the methods and their arguments from the source code.

    Args:
        source: The source code of the template

    Returns:
        A dictionary with the methods as keys and their arguments as values
    """

    result = _FUN_TEMPLATE.findall(source)
    return {
        method[1]: [x.strip() for x in method[2].split(",")]
        for method in result
    }


def _get_assoc_endpoint_name(name: str) -> str:
    """
    Get the name of the associated endpoint.

    Args:
        name: The name of the method

    Returns:
        The name of the associated endpoint
    """

    return f"_{name}"


def check_entrypoint(*, source: str) -> bool:
    """
    Check the __main__ entrypoint.

    Args:
        source: The source code of the template

    Returns:
        Success if the entrypoint is present, Failure otherwise
    """

    result = bool(_ENTRYPOINT_TEMPLATE.search(source))
    if not result:
        raise ValidationError("The __main__ entrypoint is missing")
    return result


def check_needed_methods(*, source: str, methods: Sequence[str]) -> bool:
    """
    Check if the needed methods are present in the template.

    Args:
        source: The source code of the template
        methods: The needed methods

    Returns:
        Success if the needed methods are present, Failure otherwise
    """

    parsed = _parse_defs(source)
    existing_methods = frozenset(parsed.keys())
    result = all(method in existing_methods for method in methods)

    if not result:
        raise ValidationError("The needed methods are missing")

    return result


def check_associated_endpoints(*, source: str, methods: Sequence[str]) -> bool:
    """
    Check if the needed methods associated endpoints
    are present in the template.

    Args:
        source: The source code of the template
        methods: Sequence of the methods

    Returns:
        Success if the associated endpoints are present, Failure otherwise
    """

    parsed = _parse_defs(source)
    existing_methods = frozenset(parsed.keys())

    result = all(
        _get_assoc_endpoint_name(method) in existing_methods
        for method in methods
    )
    if not result:
        raise ValidationError("The needed associated endpoints are missing")
    return result


def validate(source: str, methods: Sequence[str]):
    """
    Validate the template.

    Args:
        source: The source code of the template
        methods: Sequence of the methods

    Returns:
        Success if the template is valid, Failure otherwise
    """

    result = Fold.collect(
        (
            safe(check_needed_methods)(source=source, methods=methods),
            safe(check_associated_endpoints)(source=source, methods=methods),
            safe(check_entrypoint)(source=source),
        ),
        Success(()),
    )

    if not is_successful(result):
        raise result.failure()

    return result.unwrap()
