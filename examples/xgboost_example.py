from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from mljet import cook


# noinspection PyPep8Naming
def main():
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

    cook(strategy="local", model=bst, verbose=True)


if __name__ == "__main__":
    main()
