from catboost import CatBoostClassifier
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
    cat = CatBoostClassifier(
        iterations=2,
        depth=2,
        learning_rate=1,
        loss_function="MultiClass",
    )
    # fit model
    cat.fit(X_train, y_train)

    cook(strategy="local", model=cat, verbose=True, scan_path=__file__)


if __name__ == "__main__":
    main()
