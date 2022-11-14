from contextlib import nullcontext as does_not_raise

import pytest

# noinspection PyUnresolvedReferences,PyProtectedMember
from deployme.cookie.validator import (
    ValidationError,
    is_entrypoint_exists,
)

TEXT1 = """
def a():
    pass

def b():
    pass
"""

TEXT2 = """
def a():
    pass

if __name__ == "__main__":
    a()
"""

TEXT3 = """
def a():
    pass

# if __name__ == "__main__":
#     a()
"""

TEXT4 = """
def main():
    if ___name___ == "__main__":
        pass
"""


@pytest.mark.parametrize(
    "source, expectation",
    [
        (TEXT1, pytest.raises(ValidationError)),
        (TEXT2, does_not_raise()),
        (TEXT3, pytest.raises(ValidationError)),
        (TEXT4, pytest.raises(ValidationError)),
    ],
)
def test_check_entrypoint(source, expectation):
    with expectation:
        is_entrypoint_exists(source=source)
