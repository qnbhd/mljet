from contextlib import nullcontext as does_not_raise

import pytest

# noinspection PyUnresolvedReferences,PyProtectedMember
from mljet.cookie.validator import (
    ValidationError,
    is_needed_methods_exists,
)

TEXT1 = """
def a():
    pass
"""

TEXT2 = """
def a():
    pass

async def b():
    pass
"""


@pytest.mark.parametrize(
    "source, methods, expectation",
    [
        (TEXT1, ["a"], does_not_raise()),
        (TEXT1, ["b"], pytest.raises(ValidationError)),
        (TEXT2, ["a", "b"], does_not_raise()),
        (TEXT2, ["a", "b", "c"], pytest.raises(ValidationError)),
    ],
)
def test_check_needed_methods(source, methods, expectation):
    with expectation:
        is_needed_methods_exists(source=source, methods=methods)
