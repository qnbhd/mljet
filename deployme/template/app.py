"""Main app template."""

import logging
import os
import pickle
from dataclasses import dataclass
from typing import List

import click
import pandas as pd
import uvicorn
from blacksheep import Application
from blacksheep.server.openapi.v3 import (
    ContentInfo,
    OpenAPIHandler,
    RequestBodyInfo,
    ResponseExample,
    ResponseInfo,
)
from blacksheep.server.responses import redirect
from openapidocs.v3 import Info

MODEL_TYPE = os.getenv("MODEL_TYPE")  # ?
N_WORKERS = int(os.getenv("N_WORKERS", default="2"))

logger = logging.getLogger("deployme")
logger.setLevel(logging.INFO)

app = Application()

docs = OpenAPIHandler(info=Info(title="DeployMe", version="0.0.1"))
docs.bind_app(app)


class RenameUnpickler(pickle.Unpickler):
    def find_class(self, module: str, name: str):
        renamed_module = module
        if module == "deployme.template.base_preprocessor":
            renamed_module = "base_preprocessor"

        return super().find_class(renamed_module, name)


def pickle_loads(object_path: str):
    with open(object_path, "rb") as f:
        return RenameUnpickler(f).load()


def load_object(object_path: str):
    with open(object_path, "rb") as f:
        return pickle.load(f)


model = load_object("models/model.pkl")
example_data_path = "data/example.csv"
preprocessor_path = "models/preprocessor.pkl"
preprocessor = (
    pickle_loads(preprocessor_path)
    if os.path.isfile(preprocessor_path)
    else None
)


@dataclass
class Prediction:
    data: List[int]


@dataclass
class Objects:
    data: List[dict]


def get_predictions(data: pd.DataFrame):
    if preprocessor:
        data = preprocessor.transform(data.values)

    y_pred = model.predict(data)

    # TODO: eliminate this
    #  code block when the
    #  architecture is changed
    try:
        # noinspection PyPackageRequirements,PyUnresolvedReferences
        # pylint: disable=import-outside-toplevel
        from lightautoml.dataset.np_pd_dataset import NumpyDataset

        if isinstance(y_pred, NumpyDataset):
            y_pred = y_pred.data[:, 0]
    except ImportError:
        pass

    return y_pred


def generate_docs_example():
    if os.path.isfile(example_data_path):
        example_data = pd.read_csv(example_data_path, nrows=2)
        targets = get_predictions(example_data)
        examples = {
            "f1": Objects(data=[example_data.iloc[0].to_dict()]),
            "f2": Objects(data=[example_data.iloc[1].to_dict()]),
        }
        return examples, targets.tolist()
    else:
        return {Objects(data=[])}, []


docs_examples, docs_target = generate_docs_example()


@app.route("/predict", methods=["POST"])
@docs(
    summary="Returns a prediction for a given input",
    description="Endpoint for prediction method.",
    request_body=RequestBodyInfo(
        description="Input data for prediction",
        examples=docs_examples,
    ),
    responses={
        "200": ResponseInfo(
            "Prediction",
            content=[
                ContentInfo(
                    Prediction,
                    examples=[
                        ResponseExample(Prediction(docs_target))
                    ],
                )
            ],
        ),
    },
)
async def predict(obj: Objects) -> Prediction:
    prediction = get_predictions(pd.DataFrame.from_records(obj.data))
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
        "app:app",
        host=host,
        port=port,
        log_level="debug",
        workers=N_WORKERS,
    )
    server = uvicorn.Server(config)
    server.run()


cli.add_command(run)


if __name__ == "__main__":
    cli()
