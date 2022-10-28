import json
import os

import numpy as np
import pandas as pd
import requests
import torch
from lightautoml.automl.presets.tabular_presets import TabularAutoML
from lightautoml.tasks import Task
from sklearn.model_selection import train_test_split

from deployme.docker_ import deploy_to_docker

# Configure and fit LightAutoML model for binary classification

N_THREADS = 4
N_FOLDS = 5
RANDOM_STATE = 42
TEST_SIZE = 0.2
TIMEOUT = 300
TARGET_NAME = "TARGET"
DATASET_DIR = "../data/"
DATASET_NAME = "sampled_app_train.csv"
DATASET_FULLNAME = os.path.join(DATASET_DIR, DATASET_NAME)
DATASET_URL = (
    "https://raw.githubusercontent.com/AILab-MLTools/LightAutoML"
    "/master/examples/data/sampled_app_train.csv"
)

np.random.seed(RANDOM_STATE)
torch.set_num_threads(N_THREADS)

if not os.path.exists(DATASET_FULLNAME):
    os.makedirs(DATASET_DIR, exist_ok=True)

    dataset = requests.get(DATASET_URL).text
    with open(DATASET_FULLNAME, "w") as output:
        output.write(dataset)

data = pd.read_csv("../data/sampled_app_train.csv")

tr_data, te_data = train_test_split(
    data,
    test_size=TEST_SIZE,
    stratify=data[TARGET_NAME],
    random_state=RANDOM_STATE,
)

task = Task("binary")

roles = {"target": TARGET_NAME, "drop": ["SK_ID_CURR"]}

automl = TabularAutoML(
    task=task,
    timeout=TIMEOUT,
    cpu_limit=N_THREADS,
    reader_params={
        "n_jobs": N_THREADS,
        "cv": N_FOLDS,
        "random_state": RANDOM_STATE,
    },
)

oof_pred = automl.fit_predict(tr_data, roles=roles, verbose=1)

# Create and run docker-image
deploy_to_docker(
    model=automl,
    image_name="my_lama_service",
    data_example=te_data.head(),
)

# Test running flask-service
url = "http://127.0.0.1:5000/predict"
data = {"data": te_data.to_json()}
response = requests.post(url, json=data)
print(json.loads(response.content))
