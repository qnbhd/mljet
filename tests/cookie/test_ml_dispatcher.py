from contextlib import nullcontext as does_not_raise

import pytest

from mljet.cookie.templates.ml import dispatcher


@pytest.mark.parametrize(
    "model_type, methods, expectation",
    [
        *[
            (model_type, ["predict"], does_not_raise())
            for model_type in dispatcher.SUPPORTED_ML_KINDS
        ],
        (
            "some_not_existing_model_type",
            ["predict"],
            pytest.raises(ValueError),
        ),
    ],
)
def test_get_dual_methods(model_type, methods, expectation):
    with expectation:
        dispatcher.get_dual_methods(model_type, methods)
