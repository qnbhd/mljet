from contextlib import nullcontext as does_not_raise

import pytest

from deployme.cookie.templates.backends import dispatcher


@pytest.mark.parametrize(
    "backend_name, strict, expectation",
    [
        *[
            (backend_name, True, does_not_raise())
            for backend_name in dispatcher.SUPPORTED_BACKENDS
        ],
        ("some_not_existing_backend", True, pytest.raises(ValueError)),
        ("some_not_existing_backend", False, does_not_raise()),
    ],
)
def test_dispatch_default_backend(backend_name, strict, expectation):
    with expectation:
        dispatcher.dispatch_default_backend(backend_name, strict=strict)
