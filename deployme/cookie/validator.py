"""Static code analysis of the template."""
import logging
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

log = logging.getLogger(__name__)

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

    defs = _FUN_TEMPLATE.findall(source)
    return {
        method[1]: [arg.strip() for arg in method[2].split(",")]
        for method in defs
    }


def _get_assoc_endpoint(name: str) -> str:
    """
    Get the name of the associated endpoint.

    Args:
        name: The name of the method

    Returns:
        The name of the associated endpoint
    """

    return f"_{name}"


def is_entrypoint_exists(*, source: str) -> bool:
    """
    Check the __main__ entrypoint.

    Args:
        source: The source code of the template

    Returns:
        True if the entrypoint is present, False otherwise
    """
    log.debug("Checking the __main__ entrypoint")

    is_exists = bool(_ENTRYPOINT_TEMPLATE.search(source))
    if not is_exists:
        raise ValidationError("The __main__ entrypoint is missing")
    return is_exists


def is_needed_methods_exists(*, source: str, methods: Sequence[str]) -> bool:
    """
    Check if the needed methods are present in the template.

    Args:
        source: The source code of the template
        methods: The needed methods

    Returns:
        True if the needed methods are present, False otherwise
    """
    log.debug("Checking the needed ML model methods")

    parsed = _parse_defs(source)
    existing_methods = frozenset(parsed.keys())
    existence = all(method in existing_methods for method in methods)

    if not existence:
        raise ValidationError("The needed methods are missing")

    return existence


def is_associated_endpoints_exists(
    *, source: str, methods: Sequence[str]
) -> bool:
    """
    Check if the needed methods associated endpoints
    are present in the template.

    Args:
        source: The source code of the template
        methods: Sequence of the methods

    Returns:
        True if the associated endpoints are present, False otherwise
    """
    log.debug("Checking the associated endpoints")

    parsed = _parse_defs(source)
    existing_methods = frozenset(parsed.keys())

    is_exists = all(
        _get_assoc_endpoint(method) in existing_methods for method in methods
    )
    if not is_exists:
        raise ValidationError("The needed associated endpoints are missing")
    return is_exists


def validate(source: str, methods: Sequence[str]) -> bool:
    """
    Validate the template.

    Args:
        source: The source code of the template
        methods: Sequence of the methods

    Returns:
        True if the template is valid, False otherwise
    """

    validation_result = Fold.collect(
        (
            safe(is_needed_methods_exists)(source=source, methods=methods),
            safe(is_associated_endpoints_exists)(
                source=source, methods=methods
            ),
            safe(is_entrypoint_exists)(source=source),
        ),
        Success(()),
    )

    if not is_successful(validation_result):
        raise validation_result.failure()

    return True
