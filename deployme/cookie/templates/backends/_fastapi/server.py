"""Flask web-service, built with Deployme."""

import os
import pickle
from pathlib import Path
from typing import List

import uvicorn  # type: ignore
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class PredictRequest(BaseModel):
    data: List[List]


app = FastAPI()

with open(Path(__file__).parent.joinpath("models", "model.pkl"), "rb") as f:
    loaded_model = pickle.load(f)


# THIS CODE MUST BE REPLACED DYNAMICALLY
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


# END OF DYNAMIC CODE


@app.post("/predict")
def _predict(body: PredictRequest):
    return JSONResponse(content=predict(loaded_model, body.data))


@app.post("/predict_proba")
def _predict_proba(body: PredictRequest):
    return JSONResponse(content=predict_proba(loaded_model, body.data))


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.getenv("SERVICE_HOST", "0.0.0.0"),
        port=int(os.getenv("SERVICE_PORT", "5000")),
    )
