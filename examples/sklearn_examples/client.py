import json

import requests as requests
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from deployme.docker import deploy_to_docker


X, y = load_iris(return_X_y=True, as_frame=True)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.33
)

url = "http://127.0.0.1:5000/predict"
data = {"data": X_train.to_json(orient="records")}
response = requests.post(url, json=data)

print(response.content)
