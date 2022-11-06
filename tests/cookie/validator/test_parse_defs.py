import pytest

# noinspection PyUnresolvedReferences,PyProtectedMember
from deployme.cookie.validator import _parse_defs


@pytest.mark.parametrize(
    "source, expected",
    [
        (
            """
def foo():
    pass
""",
            {"foo": [""]},
        ),
        ("", {}),
        (
            """
async def foo(a: int, b: int) -> int:
    pass
    """,
            {"foo": ["a: int", "b: int"]},
        ),
        (
            """
def super(a: int, b) -> int:
    return a + b
async def foo(a: int, b: int) -> int:
    pass
""",
            {"foo": ["a: int", "b: int"], "super": ["a: int", "b"]},
        ),
    ],
)
def test_parse_defs(source, expected):
    assert _parse_defs(source) == expected
