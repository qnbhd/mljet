from contextlib import nullcontext as does_not_raise

import pytest

# noinspection PyUnresolvedReferences,PyProtectedMember
from deployme.cookie.validator import (
    ValidationError,
    check_needed_methods,
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
        check_needed_methods(source=source, methods=methods)
