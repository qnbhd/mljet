from pathlib import Path
from unittest import mock

import pytest
from hypothesis import (
    given,
    strategies as st,
)

# noinspection PyProtectedMember
from mljet.contrib.validator import (
    _DEFAULT_BACKEND_NAME,
    validate_ret_backend,
)
from mljet.cookie.templates.backends.dispatcher import SUPPORTED_BACKENDS


@given(backend=st.sampled_from(tuple(SUPPORTED_BACKENDS.keys())))
def test_validate_ret_backend_valid(backend):
    """Ensures that valid backend is returned."""
    assert validate_ret_backend(backend) == SUPPORTED_BACKENDS[backend]


@given(backend=st.none())
def test_validate_ret_backend_none(backend):
    """Ensures that default backend is returned."""
    assert (
        validate_ret_backend(backend)
        == SUPPORTED_BACKENDS[_DEFAULT_BACKEND_NAME]
    )


@given(backend=st.text().filter(lambda x: x not in SUPPORTED_BACKENDS))
def test_validate_ret_backend_invalid(backend):
    """Ensures that invalid backend raises an exception."""
    with mock.patch("pathlib.Path.exists", return_value=False):
        with mock.patch(
            "pathlib.Path.is_dir", return_value=False
        ), pytest.raises(ValueError):
            validate_ret_backend(backend)


@given(backend=st.text().filter(lambda x: x not in SUPPORTED_BACKENDS))
def test_validate_ret_backend_custom(backend):
    """Ensures that custom backend is returned."""
    with mock.patch("pathlib.Path.exists", return_value=True):
        with mock.patch("pathlib.Path.is_dir", return_value=True):
            assert validate_ret_backend(backend) == Path(backend)
