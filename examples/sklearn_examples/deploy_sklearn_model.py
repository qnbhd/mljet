import json

import pandas as pd
import requests
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from deployme.docker import deploy_to_docker
from deployme.template import BasePreprocessor


# Create and fit Scikit-Learn pipeline for classification task
X, y = make_classification(random_state=0)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, random_state=0
)

standard_scaler = StandardScaler()
X_train = standard_scaler.fit_transform(X_train)

clf = SVC()
clf.fit(X_train, y_train)

# Create preprocessing wrapper with scaler
custom_preprocessor = BasePreprocessor(standard_scaler)

# Create and run docker-image
deploy_to_docker(
    model=clf,
    image_name="my_sklearn_service",
    preprocessor=custom_preprocessor,
)

# Test running flask-service
url = "http://localhost:5000/predict"
data = {"data": pd.DataFrame(X_test).to_json()}
response = requests.post(url, json=data)
print(json.loads(response.content))
