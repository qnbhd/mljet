from unittest import mock

import pytest
from hypothesis import (
    given,
    strategies as st,
)

from deployme.contrib.validator import validate_ret_port


@given(port=st.none())
def test_validate_ret_port_valid(port):
    """Ensures that valid port is returned."""
    assert isinstance(validate_ret_port(port), int)


@given(port=st.integers(min_value=65536) | st.integers(max_value=-1))
def test_validate_ret_port_invalid(port):
    """Ensures that invalid port raises ValueError."""
    with pytest.raises(ValueError):
        validate_ret_port(port)


@given(port=st.integers(min_value=0, max_value=65535))
def test_validate_ret_port_in_use(port):
    """Ensures that port in use raises ValueError."""
    with mock.patch(
        "deployme.contrib.validator.is_port_in_use", return_value=False
    ):
        assert validate_ret_port(port) == port
