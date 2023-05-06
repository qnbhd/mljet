import pytest

from mljet.cookie.cutter import (
    MypyValidationError,
    mypy_run,
)


def test_mypy_run():
    text = """
def foo() -> int:
    return "abc"
"""
    with pytest.raises(MypyValidationError):
        mypy_run(text)
    text = """
def foo() -> int:
    return 1
"""
    assert mypy_run(text) == "Success: no issues found in 1 source file\n"
