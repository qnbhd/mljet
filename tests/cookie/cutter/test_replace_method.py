import re

import pytest

from mljet.cookie.cutter import replace_functions_by_names

pyfunc_with_body = re.compile(
    r"(?P<indent>[ \t]*)(async def|def)[ \t]*(?P<name>\w+)\s*\((?P<params>.*?)\)(?:[ "
    r"\t]*->[ \t]*(?P<return>\w+))?:(?P<body>(?:\n(?P=indent)(?:[ \t]+[^\n]*)|\n)+)"
)

TEXT = """def to_replace(a, b):
    return a + b


def to_replace2(a: int, b: int):
    return a - b
"""


def test_replace_method_correct():
    def to_replace(a, b):
        return a**b

    replaced = replace_functions_by_names(TEXT, {"to_replace": to_replace})
    assert (
        replaced
        == """def to_replace(a, b):
    return a**b


def to_replace2(a: int, b: int):
    return a - b
"""
    )


def test_replace_method_incorrect_name():
    def replace_method_test(a, b):
        return a + b

    with pytest.raises(ValueError):
        replace_functions_by_names(
            TEXT, {"replace_method_test": replace_method_test}
        )


def test_replace_method_no_mod_method():
    def replace_method_test(a, b):
        return a + b

    with pytest.raises(ValueError):
        replace_functions_by_names(
            TEXT, {"replace_method_test": replace_method_test}
        )


def test_incorrect_mismatched_spec():
    def to_replace(a, b, c):
        return a**b

    with pytest.raises(TypeError):
        replace_functions_by_names(TEXT, {"to_replace": to_replace})
