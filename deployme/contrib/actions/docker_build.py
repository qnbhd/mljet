"""Docker projects runner."""

import logging
import platform
import shutil
from pathlib import Path
from typing import Optional

from deployme.contrib.supported import ModelType
from deployme.contrib.validator import (
    validate_ret_container_name,
    validate_ret_port,
)
from deployme.utils import get_random_name
from deployme.utils.pipelines.stage import stage
from deployme.utils.types import Estimator

log = logging.getLogger(__name__)

_DEFAULT_BASE_IMAGE = "python:3.10"


@stage("docker-build", depends_on=["project-build"])
def docker_build(
    model: Estimator,
    tag: Optional[str] = None,
    base_image: Optional[str] = None,
    container_name: Optional[str] = None,
    need_run: bool = True,
    port: int = 5000,
    n_workers: int = 1,
    silent: bool = True,
    remove_project_dir: bool = False,
) -> str:
    """Cook docker image."""
    # Lazy docker import
    from deployme.contrib.dockerutils import (
        build_image,
        run_image,
    )

    port = validate_ret_port(port)

    log.info("🔎 Detecting base image")
    python_version = platform.python_version()
    model_type = ModelType.from_model(model)

    project_path = Path.cwd().joinpath("build")

    log.info(f"Python version detected: {python_version}")

    tag = tag or get_random_name()

    base_image = base_image or _DEFAULT_BASE_IMAGE

    build_image(
        project_path,
        tag,
        base_image=base_image,
    )

    container_name = container_name or get_random_name()
    container_name = validate_ret_container_name(container_name)

    if need_run:
        run_image(
            tag,
            model_type=model_type,
            n_workers=n_workers,
            container_name=container_name,
            port=port,
            silent=silent,
        )

    if remove_project_dir:
        shutil.rmtree(project_path, ignore_errors=True)

    return container_name
