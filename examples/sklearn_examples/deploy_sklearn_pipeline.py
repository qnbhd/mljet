import json

import pandas as pd
import requests
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from deployme.docker_ import deploy_to_docker

# Create and fit Scikit-Learn pipeline for classification task

X, y = make_classification(random_state=0)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, random_state=0
)
pipe = Pipeline([("scaler", StandardScaler()), ("svc", SVC())])
pipe.fit(X_train, y_train)

X_test = pd.DataFrame(X_test)

# Create and run docker-image
deploy_to_docker(
    model=pipe,
    image_name="my_sklearn_pipe_service",
    data_example=X_test.head(),
)

# Test running flask-service
url = "http://localhost:5000/predict"
data = {"data": X_test.to_json()}
response = requests.post(url, json=data)
print(json.loads(response.content))
