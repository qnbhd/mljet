import logging
import shutil
from pathlib import Path

import pytest
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

from mljet import cook
from mljet.utils.utils import is_package_installed

log = logging.getLogger(__name__)


@pytest.mark.skipif(
    not is_package_installed("lightgbm"), reason="LightGBM is not installed"
)
def test_cook_lightgbm():
    from lightgbm import LGBMClassifier

    data = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        data["data"], data["target"], test_size=0.2
    )
    # create model instance
    cat = LGBMClassifier()
    # fit model
    cat.fit(X_train, y_train)

    cook(
        model=cat,
        strategy="local",
        backend="sanic",
        need_run=False,
        scan_path=__file__,
    )
    assert Path("build").exists()
    shutil.rmtree("build", ignore_errors=True)
