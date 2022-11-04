from hypothesis import given
from hypothesis.strategies import sampled_from
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from deployme.contrib.supported import ModelType
from deployme.contrib.validator import validate_ret_model


@given(model=sampled_from([RandomForestClassifier(), LogisticRegression()]))
def test_validate_ret_model_valid(model):
    """Ensures that valid model is returned."""
    assert validate_ret_model(model) == ModelType.SKLEARN_MODEL


@given(model=sampled_from([Pipeline(...)]))
def test_validate_ret_model_valid_pipeline(model):
    """Ensures that valid pipeline is returned."""
    assert validate_ret_model(model) == ModelType.SKLEARN_PIPE
