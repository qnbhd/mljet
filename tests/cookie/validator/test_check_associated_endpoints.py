from contextlib import nullcontext as does_not_raise

import pytest

# noinspection PyUnresolvedReferences,PyProtectedMember
from deployme.cookie.validator import (
    ValidationError,
    _get_assoc_endpoint_name,
    check_associated_endpoints,
)

TEXT1 = f"""
def predict(model, data):
    return model.predict(data).tolist()

async def {_get_assoc_endpoint_name("predict")}(model, data):
    return ...
"""

TEXT2 = """
def predict(model, data):
    return model.predict(data).tolist()
"""

TEXT3 = f"""
def predict_proba(model, data):
    return model.predict(data).tolist()

@one
@two
@three
@spam
@eggs
def {_get_assoc_endpoint_name("predict_proba")}(model, data):
    return ...
"""


@pytest.mark.parametrize(
    "source, methods, expectation",
    [
        (TEXT1, ["predict"], does_not_raise()),
        (TEXT1, ["predict", "predict"], does_not_raise()),
        (TEXT2, ["predict"], pytest.raises(ValidationError)),
        (TEXT3, ["predict_proba"], does_not_raise()),
    ],
)
def test_check_associated_endpoints(source, methods, expectation):
    with expectation:
        check_associated_endpoints(source=source, methods=methods)
