"""Supported models types, strategies."""

from enum import Enum

from deployme.utils.types import Estimator
from deployme.utils.utils import parse_cls_name


class ModelType(str, Enum):
    """
    Model type.
    """

    # Sklearn model, such as `LogisticRegression`
    SKLEARN = "sklearn"

    # CatBoost model, such as `CatBoostClassifier`
    CATBOOST = "catboost"

    # XGB model, such as `XGBClassifier`
    XGBOOST = "xgboost"

    # LightGBM model, such as `LGBMClassifier`
    LGBM = "lightgbm"

    # LightAutoML model
    LAMA = "lightautoml"

    # In the future, we could add more types.

    @classmethod
    def from_model(cls, model: Estimator):
        """
        Get model type from model.

        Args:
            model: model to get type from

        Returns:
            Model type.
        """

        parts = parse_cls_name(model).split(".")

        mt = next(
            (
                ModelType(p)
                for p in parts
                if p in ModelType.__members__.values()
            ),
            None,
        )

        if mt:
            return mt

        raise ValueError(f"Model `{model}` now isn't supported")


# Strategy
class Strategy(str, Enum):

    # Make project or/and run container
    LOCAL = "LOCAL"
    # Make project and wrap it into Docker image
    DOCKER = "DOCKER"

    # In the future, we can add other strategies
    # like deploy to AWS Lambda, etc.
