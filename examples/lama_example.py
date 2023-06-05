import pandas as pd
from lightautoml.automl.presets.tabular_presets import TabularAutoML
from lightautoml.tasks import Task
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

from mljet import cook


# noinspection PyPep8Naming
def main():
    data = load_iris(as_frame=True)
    data = pd.concat([data["data"], data["target"]], axis=1, ignore_index=True)
    data = data.rename(columns={i: str(i) for i in data.columns})
    X_train, X_test = train_test_split(data, stratify=data["4"], test_size=0.2)
    # create model instance
    lama = TabularAutoML(
        task=Task(name="multiclass"),
        timeout=10,
    )
    # fit model
    lama.fit_predict(
        X_train,
        roles={"target": "4"},
    )

    cook(strategy="local", model=lama, verbose=True, scan_path=__file__)


if __name__ == "__main__":
    main()
