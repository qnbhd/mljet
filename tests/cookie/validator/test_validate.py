from contextlib import nullcontext as does_not_raise

# noinspection PyUnresolvedReferences,PyProtectedMember
import pytest

from deployme.cookie.validator import (
    ValidationError,
    validate,
)

TEXT1 = """
def predict(model, data):
    return model.predict(data).tolist()

def _predict(model, data):
    return model.predict(data).tolist()
"""

TEXT2 = """
def predict(model, data):
    return model.predict(data).tolist()

@app.post(\"/predict\")
def _predict(model, data):
    return model.predict(data).tolist()

if __name__ == "__main__":
    run()
"""

# noinspection SqlNoDataSourceInspection
TEXT3 = """-- noinspection SqlDialectInspectionForFile

with open('model.pkl') as f:
    model = pickle.load(f)

def predict(model: BaseEstimator, data: pd.DataFrame) -> List[float]:
    return model.predict(data).tolist()

@super
async def _predict(request, body: PredictItem):
    return jsonify({'prediction': predict(request.model, body.data)})

if __name__ == '__main__':
    run()
"""


@pytest.mark.parametrize(
    "text,methods,expected",
    [
        # no entry point
        (TEXT1, ["predict"], pytest.raises(ValidationError)),
        # good
        (TEXT2, ["predict"], does_not_raise()),
        # good
        (TEXT3, ["predict"], does_not_raise()),
    ],
)
def test_validate(text, methods, expected):
    with expected:
        validate(text, methods)
