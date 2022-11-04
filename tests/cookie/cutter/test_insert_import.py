import pytest

from deployme.cookie.cutter import insert_import


def test_insert_import():
    """Test insert_import function."""
    text = """def foo(): ..."""
    text = insert_import(text, ["bar"])
    assert (
        text
        == """import bar
def foo(): ..."""
    )
    text = insert_import(text, ["baz"])
    assert (
        text
        == """import baz
import bar
def foo(): ..."""
    )
    with pytest.raises(TypeError):
        insert_import(text, "bar")
    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        insert_import(text, 1)
    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        insert_import(text, [1, 2, 3])
