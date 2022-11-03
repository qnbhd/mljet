from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from deployme import cook


# noinspection PyPep8Naming
def main():
    X, y = load_iris(return_X_y=True, as_frame=True)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33)

    clf = RandomForestClassifier()
    clf.fit(X_train, y_train)

    cook(strategy="docker", model=clf, port=5010)


if __name__ == "__main__":
    main()
