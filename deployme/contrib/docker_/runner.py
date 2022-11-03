"""Docker projects runner."""

import logging
import platform
import shutil
from pathlib import Path

from deployme.contrib.local import local as local_runner
from deployme.contrib.supported import ModelType
from deployme.utils import get_random_name

log = logging.getLogger(__name__)


def docker(
    model,
    backend=None,
    tag=None,
    base_image=None,
    container_name=None,
    need_run=True,
    port=5000,
    scan_path=None,
    n_workers=1,
    silent=True,
    verbose=False,
    remove_project_dir=False,
):
    """Cook docker image."""
    # Lazy docker import
    from deployme.contrib.docker_.docker_builder import (
        build_image,
        run_image,
    )

    local_build_result = local_runner(
        model=model,
        backend=backend,
        port=port,
        scan_path=scan_path,
        verbose=verbose,
    )

    if not local_build_result:
        raise RuntimeError("Failed to build local project")

    log.info("🔎 Detecting base image ...")
    python_version = platform.python_version()
    model_type = ModelType.from_model(model)

    project_path = Path.cwd().joinpath("build")

    log.info(f"Python version detected: {python_version}")

    tag = tag or get_random_name()

    build_image(
        project_path,
        tag,
        base_image=base_image,
    )

    container_name = container_name or get_random_name()

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
