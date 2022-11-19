import json
import logging
import random
import shutil
import time
from pathlib import Path

import numpy.testing
import pytest
import requests
from hypothesis import (
    given,
    settings,
    strategies as st,
)
from sklearn.datasets import load_iris
from sklearn.ensemble import (
    AdaBoostClassifier,
    RandomForestClassifier,
)
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC

from deployme import cook
from deployme.cookie.templates.backends.dispatcher import SUPPORTED_BACKENDS
from deployme.utils.conn import find_free_port

log = logging.getLogger(__name__)


@given(
    model=st.sampled_from(
        [
            RandomForestClassifier(),
            AdaBoostClassifier(),
            MLPClassifier(),
            SVC(),
        ]
    ),
    backend=st.sampled_from(list(SUPPORTED_BACKENDS.keys())),
)
@settings(deadline=None)
def test_cook_classification(model, backend):
    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    model.fit(X_train, y_train)
    model.predict(X_test)
    cook(model=model, strategy="local", backend=backend, need_run=False)
    assert Path("build").exists()
    shutil.rmtree("build", ignore_errors=True)


@pytest.mark.slow
@pytest.mark.skipif(
    not shutil.which("docker"), reason="Docker is not installed"
)
@pytest.mark.parametrize(
    "model,backend",
    [
        (RandomForestClassifier(), "sanic"),
        (AdaBoostClassifier(), "flask"),
    ],
)
def test_cook_classification_docker(model, backend):
    # dirty, need to find a better way to test docker
    import docker

    port = find_free_port()

    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    model.fit(X_train, y_train)
    model.predict(X_test)

    name = f"deployme-test-{random.randint(0, 1000)}"

    container_name = cook(
        model=model,
        strategy="docker",
        container_name=name,
        port=port,
        backend=backend,
        scan_path=Path(__file__).parent,
    )

    assert container_name == name

    client = docker.from_env()
    client.containers.get(container_name)

    js = {
        "data": X_test.tolist(),
    }

    # TODO (qnbhd): Need to add healthcheck to the container
    time.sleep(10)

    log.info(f"Sending request to http://localhost:{port}/predict")
    log.info(f"Request: {json.dumps(js)}")

    response = requests.post(
        f"http://localhost:{port}/predict", json={"data": X_test.tolist()}
    )

    log.info(f"Response: {response.text}")

    numpy.testing.assert_array_equal(
        response.json(), model.predict(X_test).tolist()
    )

    assert response.status_code == 200

    client.containers.get(container_name).remove(force=True)

    assert Path("build").exists()
    shutil.rmtree("build", ignore_errors=True)
