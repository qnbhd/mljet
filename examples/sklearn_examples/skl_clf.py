from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from deployme.docker import deploy_to_docker


# noinspection PyPep8Naming
def main():
    X, y = load_iris(return_X_y=True, as_frame=True)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.33
    )

    clf = RandomForestClassifier()
    clf.fit(X_train, y_train)

    deploy_to_docker(
        model=clf,
        image_name="skl",
        port=5000,
        data_example=X_test.head(),
    )


if __name__ == "__main__":
    main()
