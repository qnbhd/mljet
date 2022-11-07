import logging
import shutil
from pathlib import Path

import pytest
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

from deployme import cook
from deployme.utils.utils import is_package_installed

log = logging.getLogger(__name__)


@pytest.mark.skipif(
    not is_package_installed("xgboost"), reason="XGBoost is not installed"
)
def test_cook_xgboost():
    from xgboost import XGBClassifier

    data = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        data["data"], data["target"], test_size=0.2
    )
    # create model instance
    bst = XGBClassifier(
        n_estimators=2,
        max_depth=2,
        learning_rate=1,
        objective="binary:logistic",
    )
    # fit model
    bst.fit(X_train, y_train)
    cook(model=bst, strategy="local", backend="sanic", need_run=False)
    assert Path("build").exists()
    shutil.rmtree("build", ignore_errors=True)
