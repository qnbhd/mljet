# DeployMe 

[![Actions Status](https://github.com/qnbhd/deployme/actions/workflows/checks.yml/badge.svg)](https://github.com/qnbhd/deployme/actions)
[![Actions Status](https://github.com/qnbhd/deployme/actions/workflows/deployme.yml/badge.svg)](https://github.com/qnbhd/deployme/actions)

If you have been working on ML models, then you have probably faced the task of deploying these models.
Perhaps you are participating in a hackathon or want to show your work to management.

According to our survey, more than `60%` of the data-scientists surveyed faced this task and more than `60%` of the respondents spent more than half an hour creating such a service.

The most common solution is to wrap it in some kind of web framework (like Flask).

Our team believes that it can be made even easier!

Our tool automatically collects all the necessary files and dependencies, creates a docker container, and launches it! And all this in one line of source code.

## Prerequisites

On your PC with local run you must have Docker & Python >= 3.7

## Installation

Install `deployme` with pip:

```bash
pip install deployme
```

or with your favorite package manager.

## Example:

```python
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from deployme import deploy_to_docker

X, y = load_iris(return_X_y=True, as_frame=True)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.33
)

clf = RandomForestClassifier()
clf.fit(X_train, y_train)

deploy_to_docker(
    model=clf,
    image_name="skl",
    data_example=X_test.head(),
)
```

After running script you can see new Docker container.
To interact with service simply open URL, logged after script running.

On this page you can see Swagger UI, test simple requests (examples included).
For direct post-requests you can use Curl:

```bash
curl -X POST "http://127.0.0.1:5001/predict" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{\"data\":[{\"sepal length (cm)\":5.8,\"sepal width (cm)\":2.7,\"petal length (cm)\":3.9,\"petal width (cm)\":1.2}]}"
```

## RoadMap:

1. Deploy to Heroku & clusters
2. Model's basic vizualization
3. Tighter integration with [LightAutoML](https://github.com/sb-ai-lab/LightAutoML)
4. Support many popular ML-frameworks, such as `XGBoost`, `TensorFlow`, `CatBoost`, etc.
5. *Your ideas!*

## Contribution:


We are always open to your contributions!
Please check our issue's and make PR.

## Our team:

* Templin Konstantin - Product Lead & SWE
* Kristina Zheltov - Idea Owner & Data Scientist
* Maxim Popov - DS/ML & PL
* Semen Zabrodin - Public relations
