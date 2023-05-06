"""Sanic web-service, built with MLJET."""

import os
import pickle
from pathlib import Path
from typing import List

from pydantic import BaseModel
from sanic import Sanic
from sanic.response import json as sanic_json
from sanic_ext import validate

app = Sanic("app")


class PredictRequest(BaseModel):
    data: List[List]


def predict(model, data) -> list:
    """
    Wrapper for `predict` method.

    Args:
        model: The model to use
        data: The data to predict

    Returns:
        The predicted class
    """
    return model.predict(data).tolist()


def predict_proba(model, data) -> list:
    """
    Wrapper for `predict_proba` method.

    Args:
        model: The model to use
        data: The data to predict

    Returns:
        Probability of each class
    """

    return model.predict_proba(data).tolist()


@app.post("/predict")
@validate(json=PredictRequest)
async def _predict(
    request, body: PredictRequest
):  # pylint: disable=unused-argument
    return sanic_json(predict(loaded_model, body.data))


@app.post("/predict_proba")
@validate(json=PredictRequest)
async def _predict_proba(
    request, body: PredictRequest
):  # pylint: disable=unused-argument
    return sanic_json(predict_proba(loaded_model, body.data))


if __name__ == "__main__":
    with open(Path(__file__).parent.joinpath("models", "model.pkl"), "rb") as f:
        loaded_model = pickle.load(f)
    app.run(
        host=os.getenv("SERVICE_HOST", "0.0.0.0"),
        port=int(os.getenv("SERVICE_PORT", "5000")),
    )
