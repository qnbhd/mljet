import json

import pytest
from hypothesis import (
    given,
    strategies as st,
)

from deployme.cli.helpers import format_info


@pytest.mark.parametrize(
    "data, expected",
    [
        (
            "soo",
            """|    | woo   |
|---:|:------|
|  0 | soo   |""",
        ),
        (
            ["soo", "boo"],
            """|    | woo   |
|---:|:------|
|  0 | soo   |
|  1 | boo   |""",
        ),
        (
            [1, 1.12],
            """|    |   woo |
|---:|------:|
|  0 |  1    |
|  1 |  1.12 |""",
        ),
    ],
)
def test_format_info_markdown(data, expected):
    assert format_info("woo", data, "markdown") == expected


@pytest.mark.parametrize(
    "data,expected",
    [
        ([1, 2, 3], "1,2,3"),
        ("str", "str"),
        ({"a": 1, "b": 2}, '{"a": 1, "b": 2}'),
        (None, "null"),
        (True, "true"),
        (1.12, "1.12"),
        (1, "1"),
    ],
)
def test_format_info_plain(data, expected):
    assert format_info("_", data, "plain") == expected


@given(
    st.text(), st.one_of(st.integers(), st.floats(), st.text(), st.booleans())
)
def test_format_info_json(name, data):
    assert format_info(name, data, "json") == json.dumps({name: data}, indent=4)
