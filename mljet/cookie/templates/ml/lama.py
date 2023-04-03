"""Module that contains LAMA model method's wrappers."""
from mljet.contrib.supported import ModelType

USED_FOR = [
    ModelType.LAMA,
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
    return model.predict(data).data.tolist()
