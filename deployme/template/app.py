from dataclasses import dataclass
import logging
import pickle
from typing import List

from blacksheep import Application
from blacksheep.server.openapi.v3 import ContentInfo
from blacksheep.server.openapi.v3 import OpenAPIHandler
from blacksheep.server.openapi.v3 import RequestBodyInfo
from blacksheep.server.openapi.v3 import ResponseExample
from blacksheep.server.openapi.v3 import ResponseInfo
from blacksheep.server.responses import redirect
import click
from openapidocs.v3 import Info
import pandas as pd
import uvicorn as uvicorn


logger = logging.getLogger("deployme")
logger.setLevel(logging.INFO)

app = Application()


docs = OpenAPIHandler(info=Info(title="DeployMe", version="0.0.1"))
docs.bind_app(app)

with open("models/model.pkl", "rb") as f:
    model = pickle.load(f)


@dataclass
class Prediction:
    data: List[int]


@dataclass
class Objects:
    data: List[dict]


@app.route("/predict", methods=["POST"])
@docs(
    summary="Returns a prediction for a given input",
    description="Endpoint for prediction method.",
    request_body=RequestBodyInfo(
        description="Input data for prediction",
        examples={
            "f1": Objects(
                data=[
                    {
                        "sepal length (cm)": 6.7,
                        "sepal width (cm)": 3.3,
                        "petal length (cm)": 5.7,
                        "petal width (cm)": 2.1,
                    }
                ]
            ),
            "f2": Objects(
                data=[
                    {
                        "sepal length (cm)": 5.0,
                        "sepal width (cm)": 3.4,
                        "petal length (cm)": 1.6,
                        "petal width (cm)": 0.4,
                    },
                ]
            ),
        },
    ),
    responses={
        "200": ResponseInfo(
            "Prediction",
            content=[
                ContentInfo(
                    Prediction,
                    examples=[ResponseExample(Prediction([0, 1, 2]))],
                )
            ],
        ),
    },
)
async def predict(obj: Objects):
    data = pd.DataFrame.from_records(obj.data)
    prediction = model.predict(data)
    return Prediction(prediction.tolist())


@app.route("/")
def main():
    return redirect("/docs")


@click.group()
def cli():
    pass


@click.command()
@click.option("--host", type=str, default="0.0.0.0")
@click.option("--port", type=int, default=5000)
def run(host, port):
    config = uvicorn.Config(
        "app:app", host=host, port=port, log_level="debug"
    )
    server = uvicorn.Server(config)
    server.run()


cli.add_command(run)

if __name__ == "__main__":
    cli()
