import itertools
import json
import logging
import os
from pathlib import Path
import pickle
import platform
import re
import shutil
import tempfile
from typing import Optional

import docker
from docker.errors import BuildError
from docker.utils.json_stream import json_stream
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.pipeline import Pipeline

from deployme.template.base_preprocessor import BasePreprocessor
from deployme.utils import copy_project_files
from deployme.utils import copy_template_files
from deployme.utils import get_random_name
from deployme.utils import merge_reqs
from deployme.utils.conn import is_port_in_use
from deployme.utils.logging_ import init
from deployme.utils.requirements import make_requirements_txt


docker_client = docker.from_env()

log = logging.getLogger(__name__)


def build_models(
    project_path: Path,
    model,
    preprocessor: Optional[BasePreprocessor],
):
    """
    Build models files.

    Args:
        project_path: path to the project
        model: model to deploy
        preprocessor: preprocessor to deploy

    Returns:
        None

    Raises:
        Exception: if model is not an instance of BaseEstimator

    """
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


def build_requirements(project_path: Path, scan_path: Path):
    """
    Build requirements.txt file.

    Args:
        project_path: path to the project
        scan_path: path to scan for dependencies

    Returns:
        None

    Raises:
        Exception: if requirements.txt already exists
    """

    project_reqs_path = str(project_path / "requirements.txt")
    pipreqsnb_reqs_path = str(
        project_path.parent / "requirements.txt"
    )

    log.info("☕ Cooking requirements ...")

    requirements = make_requirements_txt(
        scan_path, ignore_mods=["deployme"]
    )

    log.info("I found the following requirements:")

    log.info(f"{json.dumps(requirements, indent=4)}")

    merge_reqs(
        project_reqs_path, pipreqsnb_reqs_path, project_reqs_path
    )

    if os.path.isfile(pipreqsnb_reqs_path):
        os.remove(pipreqsnb_reqs_path)


def build_data(project_path: Path, example_data: pd.DataFrame):
    """
    Build data files.

    Args:
        project_path: path to the project
        example_data: example data to deploy

    Returns:
        None

    Raises:
        Exception: if example_data is not a DataFrame
    """

    data_path = project_path / "data"
    data_path.mkdir(exist_ok=True, parents=True)
    example_data.to_csv(str(data_path / "example.csv"), index=False)


def build_project_files(
    model,
    preprocessor: Optional[BasePreprocessor],
    example_data: pd.DataFrame,
    scan_path: Path,
) -> Path:
    """
    Build project files.

    Args:
        model: model to deploy
        preprocessor: preprocessor to deploy
        example_data: example data to deploy
        scan_path: path to scan for dependencies

    Returns:
        path to the project

    Raises:
        Exception: if model is not an instance of BaseEstimator

    """

    project_path = Path.cwd() / "project"
    project_path.mkdir(exist_ok=True, parents=True)
    build_models(project_path, model, preprocessor)
    build_data(project_path, example_data)

    templates_path = Path(__file__).parent.parent / "template"
    copy_template_files(project_path, templates_path)

    build_requirements(project_path, scan_path)

    return project_path


def build_image(
    project_path: Path,
    image_name: str,
    base_image: str,
    log_level: str = "INFO",
):
    """
    Build a Docker image with the project.

    Args:
        project_path: path to the project
        image_name: name of the image to build
        base_image: base image to build on
        log_level: logging level to set up logger

    Returns:
        None
    """
    log.setLevel(log_level)
    log.info("🍻 Building Docker image ...")

    build_streamer = docker_client.api.build(
        buildargs={"BASE_IMAGE": base_image},
        tag=image_name,
        path=str(project_path),
        forcerm=True,
        nocache=True,
        pull=True,
    )

    json_stream_value = json_stream(build_streamer)
    result_stream, internal_stream = itertools.tee(json_stream_value)
    for chunk in result_stream:
        if "error" in chunk:
            raise BuildError(chunk["error"], result_stream)
        if "stream" in chunk:
            match = re.search(
                r"(^Successfully built |sha256:)([0-9a-f]+)$",
                chunk["stream"],
            )
            if match:
                image_id = match.group(2)
        last_event = chunk
        if "stream" in chunk or "status" in chunk:
            log_message = chunk.popitem()[1].strip("\n")
            if "Step" in log_message:
                log.info(log_message)
            elif log_message:
                log.debug(log_message)

    if not image_id:
        raise BuildError(last_event or "Unknown", result_stream)


def run_image(
    image_name: str,
    model_type: str,
    n_workers: int,
    container_name: str,
    port: int = 5000,
    silent=True,
):
    """
    Run a Docker image with the project.

    Args:
        image_name: name of the image to run
        model_type: type of the model to run
        n_workers: number of workers to run
        container_name: name of the container to run
        port: port to run
        silent: if True, run container in the background

    Raises:
        Exception: if container with the same name already exists

    """

    log.info(f"🐳 Running container {container_name} ...")

    container = docker_client.containers.run(
        image=image_name,
        environment={
            "MODEL_TYPE": model_type,
            "N_WORKERS": n_workers,
        },
        name=container_name,
        ports={"5000": port},
        detach=True,
    )

    if silent:
        log.info(f"🚀 Service running on http://127.0.0.1:{port}")
        return

    to_drop = ["INFO:", "WARNING:", "ERROR:", "CRITICAL:"]

    # noinspection PyBroadException
    try:
        for line in container.logs(stream=True):
            decoded = line.decode("utf-8")

            for drop in to_drop:
                decoded = decoded.replace(drop, "")

            if "running on" in decoded:
                log.info(
                    f"🚀 Running on http://127.0.0.1:{port} (Press CTRL+C to quit)"
                )
            else:
                log.info(decoded.strip())
    except KeyboardInterrupt:
        log.info("Removing container ...")
        container.kill()
        container.remove()
    finally:
        log.info("Service is closed! Bye ...")


def deploy_to_docker(
    model,
    image_name: str,
    data_example: pd.DataFrame,
    base_image=None,
    container_name: Optional[str] = None,
    need_run: bool = True,
    port: int = 5000,
    preprocessor: Optional[BasePreprocessor] = None,
    n_workers: int = 4,
    silent=True,
    verbose=False,
    scan_path=None,
    remove_project_dir=False,
    log_level: str = "INFO",
):
    """
    Deploy model.

    Args:
        model: model to deploy
        image_name: name of the image to build
        data_example: example data to deploy
        base_image: base image to build on
        base_image: base image to build on, defaults
            to auto-detect.
        container_name: name of the container to run
        need_run: if True, run container after building
        port: port to run
        preprocessor: preprocessor to deploy
        n_workers: number of workers to run
        silent: if True, run container in the background
        verbose: if True, show verbose logs
        scan_path: path to scan for dependencies
        remove_project_dir: if True, remove project directory after building
        log_level: logging level to set up logger

    Returns:
        Container name.

    """

    init(verbose=verbose)

    if is_port_in_use(port):
        raise Exception(f"Port {port} is already in use")

    if "lightautoml" in str(type(model)):
        model_type = "LAMA"
    elif isinstance(model, Pipeline):
        model_type = "sklearn_pipe"
    elif isinstance(model, BaseEstimator):
        model_type = "sklearn_model"
        if preprocessor is None:
            log.debug(
                "If you'd like to use a raw data as API input, you could provide preprocessor object"
                " callable object with preprocess data logic. Otherwise your API will accept only"
                " preprocessed data as an input."
            )
    else:
        raise ValueError("Model type is not supported")

    log.info("🔨 Сopying project files ...")

    scan_path = Path(scan_path) if scan_path else Path.cwd()

    project_path = build_project_files(
        model, preprocessor, data_example, scan_path=scan_path
    )

    log.info(f"🏠 Project directory: {project_path}")

    log.info("🔎 Detecting base image ...")
    python_version = platform.python_version()

    log.info(f"Python version detected: {python_version}")
    base_image = base_image or f"python:{python_version}"

    build_image(
        project_path,
        image_name,
        base_image=base_image,
        log_level=log_level,
    )

    container_name = container_name or get_random_name()

    if need_run:
        run_image(
            image_name,
            model_type=model_type,
            n_workers=n_workers,
            container_name=container_name,
            port=port,
            silent=silent,
        )

    if remove_project_dir:
        shutil.rmtree(project_path, ignore_errors=True)

    return container_name
