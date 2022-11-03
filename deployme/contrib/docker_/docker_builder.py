"""Docker build module."""

import logging
import re
import signal
from pathlib import Path

import docker
import pandas as pd

docker_client = docker.from_env()

log = logging.getLogger(__name__)

_URL_REGEX = re.compile(
    r"https?://(www\.)?[-a-zA-Z\d@:%._+~#=]{1,256}\.[a-zA-Z\d()]"
    r"{1,6}\b([-a-zA-Z\d()@:%_+.~#?&/=]*)"
)


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


def build_image(project_path: Path, image_name: str, base_image: str):
    """
    Build a Docker image with the project.

    Args:
        project_path: path to the project
        image_name: name of the image to build
        base_image: base image to build on

    Returns:
        None
    """

    log.info("🍻 Building Docker image ...")

    docker_client.images.build(
        buildargs={"BASE_IMAGE": base_image},
        tag=image_name,
        path=str(project_path),
        rm=True,
    )


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

    def teardown():
        log.info("👋 Stopping container ...")
        container.kill()
        container.remove()
        log.info("👋 Container stopped")

    signal.signal(signal.SIGHUP, lambda *_: teardown())
    signal.signal(signal.SIGTERM, lambda *_: teardown())

    to_drop = ["INFO:", "WARNING:", "ERROR:", "CRITICAL:"]

    # noinspection PyBroadException
    try:
        for line in container.logs(stream=True):
            decoded = line.decode("utf-8")

            for drop in to_drop:
                decoded = decoded.replace(drop, "")

            if _URL_REGEX.search(decoded):
                log.info(f"🚀 Service running on http://127.0.0.1:{port}")
            else:
                log.info(decoded.strip())
    except KeyboardInterrupt:
        teardown()
    finally:
        log.info("Service is closed! Bye ...")
