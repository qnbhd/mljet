import os
from pathlib import Path
import pickle
import shutil
import tempfile
from typing import Optional
import warnings

import pandas as pd
from pipreqsnb import pipreqsnb
from sklearn.base import BaseEstimator
from sklearn.pipeline import Pipeline

from deployme.template.base_preprocessor import BasePreprocessor
from deployme.utils import copy_project_files
from deployme.utils import copy_template_files
from deployme.utils import get_random_name
from deployme.utils import merge_reqs
from deployme.utils.logging import init
import docker


init(verbose=True)

BASE_IMAGE = "python:3.10-slim-bullseye"

docker_client = docker.from_env()


def build_models(
    project_path: Path, model, preprocessor: BasePreprocessor
) -> None:
    models_path = tempfile.mkdtemp()
    model_path = f"{models_path}/model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    if preprocessor is not None:
        preprocessor_path = f"{models_path}/preprocessor.pkl"
        with open(preprocessor_path, "wb") as f:
            pickle.dump(preprocessor, f)

    copy_project_files(
        project_path, old_path=models_path, folder_name="models"
    )
    shutil.rmtree(models_path)


def build_requirements(project_path: Path) -> None:
    project_reqs_path = str(project_path / "requirements.txt")
    pipreqsnb_reqs_path = str(
        project_path.parent / "requirements.txt"
    )

    pipreqsnb.main()
    merge_reqs(project_reqs_path, pipreqsnb_reqs_path)
    shutil.move(
        f'{str(project_path.parent / "requirements-merged.txt")}',
        project_reqs_path,
    )
    if os.path.isfile(pipreqsnb_reqs_path):
        os.remove(pipreqsnb_reqs_path)


def build_data(
    project_path: Path, example_data: pd.DataFrame
) -> None:
    data_path = project_path / "data"
    data_path.mkdir(exist_ok=True, parents=True)
    example_data.to_csv(str(data_path / "example.csv"), index=False)


def build_project_files(
    model, preprocessor: BasePreprocessor, example_data: pd.DataFrame
) -> str:
    project_path = Path.cwd() / "project"
    project_path.mkdir(exist_ok=True, parents=True)
    build_models(project_path, model, preprocessor)
    build_data(project_path, example_data)

    templates_path = Path(__file__).parent.parent / "template"
    copy_template_files(project_path, templates_path)

    build_requirements(project_path)
    return str(project_path)


def build_image(
    project_path: str, image_name: str, base_image: str
) -> None:
    """Build a Docker image for the project."""
    docker_client.images.build(
        buildargs={"BASE_IMAGE": base_image},
        tag=image_name,
        path=project_path,
    )


def run_image(
    image_name: str,
    model_type: str,
    n_workers: int,
    container_name: Optional[str] = None,
    port: int = 5000,
) -> None:
    """Run builded Docker image."""
    container_name = (
        container_name if container_name else get_random_name()
    )
    docker_client.containers.run(
        image=image_name,
        environment={
            "MODEL_TYPE": model_type,
            "N_WORKERS": n_workers,
        },
        name=container_name,
        ports={"5000": port},
        detach=True,
    )


def deploy_to_docker(
    model,
    image_name: str,
    data_example: pd.DataFrame,
    base_image: str = BASE_IMAGE,
    container_name: Optional[str] = None,
    need_run: bool = True,
    port: int = 5000,
    preprocessor: Optional[BasePreprocessor] = None,
    n_workers: int = 4,
) -> None:
    if "lightautoml" in str(type(model)):
        model_type = "LAMA"
    elif isinstance(model, Pipeline):
        model_type = "sklearn_pipe"
    elif isinstance(model, BaseEstimator):
        model_type = "sklearn_model"
        if preprocessor is None:
            warnings.warn(
                "If you'd like to use a raw data as API input, you could provide preprocessor object"
                "callable object with preprocess data logic. Otherwise your API will accept only "
                "preprocessed data as an input."
            )

    project_path = build_project_files(
        model, preprocessor, data_example
    )

    build_image(
        project_path,
        image_name,
        base_image=base_image,
    )

    if need_run:
        run_image(
            image_name,
            model_type=model_type,
            n_workers=n_workers,
            container_name=container_name,
            port=port,
        )
    shutil.rmtree(project_path)
