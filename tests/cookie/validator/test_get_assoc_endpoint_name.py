# noinspection PyUnresolvedReferences,PyProtectedMember
from hypothesis import given
from hypothesis.strategies import text

from deployme.cookie.validator import _get_assoc_endpoint_name


@given(text())
def test_get_assoc_endpoint_name(s):
    assert _get_assoc_endpoint_name(s) == f"_{s}"
