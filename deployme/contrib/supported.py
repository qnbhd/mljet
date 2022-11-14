"""Supported models types, strategies."""

from enum import Enum

from sklearn.base import BaseEstimator
from sklearn.pipeline import Pipeline

from deployme.utils.types import Estimator


class ModelType(str, Enum):
    """
    Model type.
    """

    # LightAutoML model
    LAMA = "LAMA"

    # Sklearn pipeline, such as `Pipeline`
    SKLEARN_PIPE = "SKLEARN_PIPELINE"

    # Sklearn model, such as `LogisticRegression`
    SKLEARN_MODEL = "SKLEARN_MODEL"

    # In the future, we could add more types,
    # such as `XGBoost` or `CatBoost`

    @classmethod
    def from_model(cls, model: Estimator):
        """
        Get model type from model.

        Args:
            model: model to get type from

        Returns:
            Model type.
        """

        if "lightautoml" in str(type(model)):
            return cls.LAMA

        if isinstance(model, Pipeline):
            return cls.SKLEARN_PIPE

        if isinstance(model, BaseEstimator):
            return cls.SKLEARN_MODEL

        raise ValueError(f"Model `{model}` now isn't supported")


# Strategy
class Strategy(str, Enum):

    # Make project or/and run container
    LOCAL = "LOCAL"
    # Make project and wrap it into Docker image
    DOCKER = "DOCKER"

    # In the future, we can add other strategies
    # like deploy to AWS Lambda, etc.
