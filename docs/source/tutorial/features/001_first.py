"""
.. _first:

1. Lightweight and versatile
=============================================================

DeployMe is written entirely in Python with few dependencies.
This means that once you get interested in DeployMe, we can quickly move to a practical example.


Simple Sklearn Local Example
----------------------------

DeployMe provides a simple interface to create project and deploy a model.

- :func:`deployme.contrib.entrypoint.cook` is a function that takes a model and a strategy and deploys it.

In this example, we simply create a project with scikit-learn.
"""


###################################################################################################
# Firstly, import :mod:`deployme`.


from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

import deployme

###################################################################################################
# Import :class:`sklearn.ensemble.RandomForestClassifier` as classifier
# and :mod:`sklearn.datasets` to load the iris dataset.




###################################################################################################
# Let's load dataset and create and train a simple model.


X, y = load_iris(return_X_y=True)
clf = RandomForestClassifier()
clf.fit(X, y)


###################################################################################################
# Now, we can deploy the model with :func:`deployme.contrib.entrypoint.cook`.
# Main arguments are ``model`` and ``strategy``.
#
# The strategy can be either `local` or `docker`.
# The `local` strategy will deploy the model locally.
# The `docker` strategy will deploy the model in a docker container.
# The :func:`deployme.contrib.entrypoint.cook` function will return a bool or container name.
#
# Now we make only a project without running it.
# After calling the :func:`deployme.contrib.entrypoint.cook` function
# You can see `build` folder in the current directory.
#
# It contains:
#
# - `Dockerfile` - Dockerfile for the model
#
# - `requirements.txt` - requirements for the model
#
# - `models` directory - directory with the dumped model
#
# - `data` directory - directory with the example for the model
#
# - `server.py` - main file for the model
#

deployme.contrib.cook(strategy="local", model=clf)

###################################################################################################
# Let's see on :func:`deployme.contrib.entrypoint.cook` signature.
# This function accepts a lot of parameters, but we see only the most important ones.
#
# - `model` - model to deploy
# - `strategy` - strategy to use
# - `backend` - backend to use
# - `need_run` - run service after build or not
# - `scan_path` - path to scan for requirements
# - `silent` - silent mode
# - `verbose` - verbose mode
#
# Model parameter is the most important one.
# It can be any model that implements the `predict` and other methods.
#
# .. note::
#     The model must be picklable.
#
# .. note::
#     Now is supported `sklearn`, `xgboost`.
#
# Strategy parameter determines the strategy to use.
#
# Backend parameter determines the backend to use.
# Now is implemented :mod:`sanic` and :mod:`flask` backends.
