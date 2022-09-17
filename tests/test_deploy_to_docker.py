import logging
from time import sleep

import docker
import pytest
import requests
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from deployme import deploy_to_docker

# noinspection PyPep8Naming
from deployme.utils.conn import find_free_port


log = logging.getLogger(__name__)


# noinspection PyPep8Naming
@pytest.mark.slow
def test_deploy_to_docker_sklearn():
    X, y = load_iris(return_X_y=True, as_frame=True)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.33
    )

    clf = RandomForestClassifier()
    clf.fit(X_train, y_train)

    free_port = find_free_port()

    # run silently
    container_name = deploy_to_docker(
        model=clf,
        image_name="skl",
        port=free_port,
        data_example=X_test.head(),
        scan_path=__file__,
    )

    json = {
        "data": [
            {
                "sepal length (cm)": 5.8,
                "sepal width (cm)": 2.7,
                "petal length (cm)": 5.1,
                "petal width (cm)": 1.9,
            }
        ]
    }

    log.info(
        "Waiting for service completely start (sleep for 5s) ..."
    )
    sleep(5)

    response = requests.post(
        f"http://127.0.0.1:{free_port}/predict",
        json=json,
    )

    assert response.status_code == 200

    client = docker.from_env()
    container = client.containers.get(container_name)
    container.kill()
    container.remove()
