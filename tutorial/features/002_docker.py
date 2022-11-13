"""
.. _docker:

2. Deploy with Docker
=============================================================

In this example, we deploy the model with Docker.
For this example you need to install Docker, see `Docker <https://docs.docker.com/get-docker/>`_
and XGBoost, see `XGBoost <https://xgboost.readthedocs.io/en/latest/build.html>`_.
"""


###################################################################################################
# Firstly, import :mod:`deployme`.


import deployme

###################################################################################################
# Import :class:`xgboost.XGBClassifier` as classifier
# and :mod:`sklearn.datasets` to load the iris dataset.

from sklearn.datasets import load_iris
from xgboost import XGBClassifier


###################################################################################################
# Let's load dataset and create and train a simple model.


X, y = load_iris(return_X_y=True)
clf = XGBClassifier()
clf.fit(X, y)


###################################################################################################
# Now, we can deploy the model to `docker` with :func:`deployme.contrib.entrypoint.cook`.

deployme.contrib.cook(
    model=clf,
    strategy="docker",
    tag="deployme-xgboost",
    port=5000,
    need_run=True,
    silent=True,
    verbose=False,
)

###################################################################################################
# Let's see on passed parameters.
#
# - `model` - model to deploy - `clf` (XGBoost model)
#
# - `strategy` - strategy to use - `docker`
#
# - `tag` - tag for the docker image - `deployme-xgboost`
#
# - `port` - port for the docker container - `8000`
#
# - `backend` - backend to use - `sanic`, see `Sanic <https://sanicframework.org/>`_
#
# - `need_run` - run service after build or not - `True` (only create container)
#
# - `silent` - silent mode - `True`, non-blocking mode
#
# - `verbose` - verbose mode - `True`, print DEBUG logs
#
# After calling the :func:`deployme.contrib.entrypoint.cook` function
# You can see `build` folder in the current directory.
# And you can see the docker image and container with name `deployme-xgboost`.
#
# Now we can send a request to the model.
# For this example, we use requests, see `Requests <https://requests.readthedocs.io/en/master/>`_.
# You can use any other tool, for example `Postman <https://www.postman.com/>`_.
# Firstly, import requests.

import time

import requests

###################################################################################################
# Let's sleep for 5 seconds and check the response.


time.sleep(5)

response = requests.post(
    "http://localhost:5000/predict",
    json={"data": X.tolist()},
)

print(response.json())
