from lightgbm import LGBMClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

from mljet import cook


# noinspection PyPep8Naming
def main():
    data = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        data["data"], data["target"], test_size=0.2
    )
    # create model instance
    lgbm = LGBMClassifier(
        n_estimators=2,
        max_depth=2,
        learning_rate=1,
    )
    # fit model
    lgbm.fit(X_train, y_train)

    cook(strategy="local", model=lgbm, verbose=True, scan_path=__file__)


if __name__ == "__main__":
    main()
