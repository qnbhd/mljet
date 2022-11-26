from pathlib import Path

import pytest
from hypothesis import (
    given,
    settings,
    strategies as st,
)
from packaging.version import parse

from deployme.utils.requirements import (
    _ComparableRequirement,
    merge,
    merge_requirements_txt,
)


@given(
    x=st.lists(
        st.from_regex(r"numpy==[0-9]\.[0-9]\.[0-9]", fullmatch=True),
        min_size=1,
        max_size=5,
    ),
)
@settings(deadline=None)
def test_merge(x):
    merge_result = merge(x)
    versions = (parse(r.split("==")[1]) for r in merge_result)
    minima = min(versions)
    package_minima = f"numpy=={minima}"
    assert [package_minima] == merge_result


@pytest.mark.repeat(5)
def test_merge_requirements_txt():
    requirements_dir = Path(__file__).parent.joinpath("requirements-examples")
    left = requirements_dir.joinpath("backend-requirements.txt")
    right = requirements_dir.joinpath("freezed-requirements.txt")
    result = merge_requirements_txt(left, right)
    assert result == [
        "aiofiles==22.1.0",
        "aiohttp==3.8.3",
        "aiosignal==1.3.1",
        "alabaster==0.7.12",
        "flask-pydantic==0.11.0",
        "flask==2.2.2",
        "flit-core==3.8.0",
        "fonttools==4.38.0",
        "frozenlist==1.3.3",
        "furo==2022.9.29",
        "gitdb==4.0.9",
        "gitpython==3.1.29",
        "greenlet==2.0.1",
        "gunicorn==20.1.0",
        "httptools==0.5.0",
        "hypothesis==6.56.4",
        "identify==2.5.8",
        "idna==3.4",
        "imagesize==1.4.1",
        "importlib-metadata==5.0.0",
        "iniconfig==1.1.1",
        "invoke==1.7.3",
        "isort==5.10.1",
        "iterfzf==0.5.0.20.0",
        "itsdangerous==2.1.2",
        "jaraco.classes==3.2.3",
        "jeepney==0.8.0",
        "jinja2==3.1.2",
        "pydantic==1.10.2",
        "yattag==1.14.0",
        "zipp==3.10.0",
    ]


# Now supported only `==` operator
@given(
    x=st.lists(
        st.from_regex(r"numpy(<=|>=|>|<)[0-9]\.[0-9]\.[0-9]", fullmatch=True),
        min_size=1,
    ),
)
@settings(deadline=None)
def test_merge_not_pinned(x):
    with pytest.raises(ValueError):
        merge(x)


@given(
    x=st.from_regex(r"numpy==[0-9]\.[0-9]\.[0-9]", fullmatch=True),
    y=st.from_regex(r"numpy==[0-9]\.[0-9]\.[0-9]", fullmatch=True),
)
@settings(deadline=None)
def test_merge_idempotent(x, y):
    assert merge([x], [y]) == merge(merge([x], [y]))


@given(
    x=st.from_regex(r"numpy==[0-9]\.[0-9]\.[0-9]", fullmatch=True),
    y=st.from_regex(r"numpy==[0-9]\.[0-9]\.[0-9]", fullmatch=True),
    z=st.from_regex(r"numpy==[0-9]\.[0-9]\.[0-9]", fullmatch=True),
)
@settings(deadline=None)
def test_merge_associative(x, y, z):
    assert (
        merge([x], [y], [z])
        == merge([x], merge([y], [z]))
        == merge(merge([x], [y]), [z])
    )


@given(
    x=st.lists(
        st.from_regex(r"[a-z]+==[0-9]\.[0-9]\.[0-9]", fullmatch=True),
        min_size=1,
        max_size=5,
    ),
    y=st.lists(
        st.from_regex(r"[a-z]+==[0-9]\.[0-9]\.[0-9]", fullmatch=True),
        min_size=1,
        max_size=5,
    ),
)
@settings(deadline=None)
def test_commutative(x, y):
    assert set(merge(x, y)) == set(merge(y, x))


def test_comparison():
    a = _ComparableRequirement("numpy==1.2.3")
    b = _ComparableRequirement("numpy==1.2.4")
    c = _ComparableRequirement("numpy==1.2.3")
    assert a == a
    assert a < b
    assert a == c
    assert b > a
    assert b > c
    assert c < b
    assert a <= b
    assert c >= a
    assert a != b


def test_comparable_str():
    a = _ComparableRequirement("numpy==1.2.3")
    assert str(a) == "numpy==1.2.3"
