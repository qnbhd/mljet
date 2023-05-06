"""Flask web-service, built with MLJET."""

import os
import pickle
from pathlib import Path
from typing import List

from aiohttp import web
from pydantic import BaseModel


class PredictRequest(BaseModel):
    data: List[List]


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


async def _predict(self, request: PredictRequest):
    prediction = predict(loaded_model, request.data)
    return web.json_response(prediction)


async def _predict_proba(self, request: PredictRequest):
    prediction = predict_proba(loaded_model, request.data)
    return web.json_response(prediction)


app = web.Application()
app.router.add_post("/predict_proba", _predict_proba)  # type: ignore
app.router.add_post("/predict", _predict)  # type: ignore

if __name__ == "__main__":
    web.run_app(
        app,
        host=os.getenv("SERVICE_HOST", "0.0.0.0"),
        port=int(os.getenv("SERVICE_PORT", "5000")),
    )
