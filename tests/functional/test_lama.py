import logging
import shutil
import sys
from pathlib import Path

import pandas as pd
import pytest
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

from mljet import cook
from mljet.utils.utils import is_package_installed

log = logging.getLogger(__name__)


@pytest.mark.skipif(
    not is_package_installed("lightautoml"),
    reason="LightAutoML is not installed",
)
@pytest.mark.skipif(
    sys.version_info >= (3, 10), reason="Lama requires python < 3.10"
)
def test_cook_lama():
    from lightautoml.automl.presets.tabular_presets import TabularAutoML
    from lightautoml.tasks import Task

    data = load_iris(as_frame=True)
    data = pd.concat([data["data"], data["target"]], axis=1, ignore_index=True)
    data = data.rename(columns={i: str(i) for i in data.columns})
    X_train, X_test = train_test_split(data, stratify=data["4"], test_size=0.2)
    # create model instance
    lama = TabularAutoML(
        task=Task(name="multiclass"),
        timeout=10,
    )
    lama.fit_predict(
        X_train,
        roles={"target": "4"},
    )

    cook(
        model=lama,
        strategy="local",
        backend="sanic",
        need_run=False,
        scan_path=__file__,
    )
    assert Path("build").exists()
    shutil.rmtree("build", ignore_errors=True)
