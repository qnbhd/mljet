.. deployme documentation master file, created by
   sphinx-quickstart on Mon Nov  7 08:45:51 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to deployme's documentation!
====================================

.. raw:: html
   :file: deployme-logo-p.svg

DeployMe
===============================================

DeployMe - a minimalistic tool for automatic deployment of machine learning models.

Key Features
------------

* Light-weight, cross-platform
* Simple pythonic interface
* Ability to wrap models locally in a service or in a docker container
* Support for multiple model formats
* Support for difference web-frameworks
* Independence of final projects from this tool

Code example
--------------

.. code:: python

   from sklearn.datasets import load_iris
   from sklearn.ensemble import RandomForestClassifier

   from deployme import cook

   X, y = load_iris(return_X_y=True, as_frame=True)

   clf = RandomForestClassifier()
   clf.fit(X, y)

   cook(strategy="docker", model=clf, port=5001)

After running script you can see new Docker container. To interact with service simply use CURL:

.. code:: bash

   curl -X POST "http://127.0.0.1:5001/predict" -H  "accept: application/json" -H  "Content-Type: application/json" -d '{\"data\":[[5.8, 2.7, 3.9, 1.2]]}'

Communication
-------------

-  `GitHub Issues <https://github.com/qnbhd/deployme/issues>`__ for bug
   reports, feature requests and questions.

License
-------

MIT License (see `LICENSE <https://github.com/qnbhd/deployme/blob/master/LICENSE>`__).

Authors
---------

Templin Konstantin <1qnbhd@gmail.com>

Kristina Zheltova <masterkristall@gmail.com>

Contents
==================

.. toctree::
   :maxdepth: 2

   installation
   reference/index
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
