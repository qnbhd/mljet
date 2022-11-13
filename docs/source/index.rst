.. deployme documentation master file, created by
   sphinx-quickstart on Mon Nov  7 08:45:51 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to deployme's documentation!
====================================

.. figure:: deployme-logo-p.svg
    :align: center

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

Pipeline
--------

.. figure:: images/pipeline.svg
    :align: center

    Pipeline

- First, we initialize the project directory for the next steps;
- Next, we serialize your machine learning models (for example, with Joblib or Pickle);
- Next, we create a final .py file based on the templates that contains the endpoint handlers. Handlers are chosen based on models, and templates based on your preferences (templates are also .py files using, for example, Sanic or Flask);
- Copy or additionally generate the necessary files (e.g. Dockerfile);
- The next step is to compile the API documentation for your project;
- After these steps, we build a Docker container, or a Python package, or we just leave the final directory and then we can deploy your project in Kubernetes, or in Heroku.


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


.. toctree::
   :maxdepth: 1
   :hidden:

   installation
   tutorial/index
   developers-guide/index
   reference/index
   changelog
