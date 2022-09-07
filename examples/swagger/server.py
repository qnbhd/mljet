from dataclasses import dataclass
from typing import List

from blacksheep import Application
from blacksheep.server.openapi.v3 import ContentInfo
from blacksheep.server.openapi.v3 import OpenAPIHandler
from blacksheep.server.openapi.v3 import RequestBodyInfo
from blacksheep.server.openapi.v3 import ResponseExample
from blacksheep.server.openapi.v3 import ResponseInfo
from openapidocs.v3 import Info
import uvicorn as uvicorn


app = Application()

docs = OpenAPIHandler(info=Info(title="DeployMe", version="0.0.1"))
docs.bind_app(app)


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
            "foo": Objects(
                data=[
                    {
                        "sepal length (cm)": 0,
                        "sepal width (cm)": 0,
                        "petal length (cm)": 0,
                        "petal width (cm)": 0,
                    }
                ]
            )
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
    return Prediction([0, 1, 2])


if __name__ == "__main__":
    config = uvicorn.Config("server:app", port=5000, log_level="info")
    server = uvicorn.Server(config)
    server.run()
