"""Module that contains Scikit-learn model method's wrappers."""
from deployme.contrib.supported import ModelType

USED_FOR = [
    ModelType.SKLEARN,
    ModelType.XGBOOST,
    ModelType.CATBOOST,
    ModelType.LGBM,
]


def predict(model, data) -> list:
    """
    Wrapper for `predict` method.

    Args:
        model: The model to use
        data: The data to predict

    Returns:
        The predicted class
    """
    return model.predict(data).tolist()


def predict_proba(model, data) -> list:
    """
    Wrapper for `predict_proba` method.

    Args:
        model: The model to use
        data: The data to predict

    Returns:
        Probability of each class
    """

    return model.predict_proba(data).tolist()
