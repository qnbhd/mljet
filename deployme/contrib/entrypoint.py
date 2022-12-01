"""Docker builder module."""

import logging
from typing import (
    Optional,
    Sequence,
    Union,
)

from returns.pipeline import is_successful
from returns.result import safe

from deployme.contrib.actions.docker_build import docker_build
from deployme.contrib.actions.project_build import project_build
from deployme.contrib.supported import Strategy
from deployme.contrib.validator import validate_ret_strategy
from deployme.utils.pipelines.pipeline import (
    Context,
    Pipeline,
    RunResult,
)
from deployme.utils.types import PathLike

log = logging.getLogger(__name__)


def cook(
    *,
    model,
    strategy: Union[Strategy, str] = Strategy.DOCKER,
    backend: Optional[Union[str, PathLike]] = None,
    tag: Optional[str] = None,
    base_image: Optional[str] = None,
    container_name: Optional[str] = None,
    need_run: bool = True,
    port: Optional[int] = None,
    scan_path: Optional[PathLike] = None,
    n_workers: int = 1,
    silent: bool = True,
    verbose: bool = False,
    remove_project_dir: bool = False,
    ignore_mypy: bool = False,
    additional_requirements_files: Optional[Sequence[PathLike]] = None,
) -> RunResult:
    """
    Cook web-service.

    Args:
        model: model to deploy
        strategy: strategy to use
        backend: backend to use
        tag: tag for docker image
        base_image: base image for docker image
        container_name: container name
        need_run: run service after build or not
        port: port to use
        scan_path: path to scan for requirements
        n_workers: number of workers
        silent: silent mode
        verbose: verbose mode
        remove_project_dir: remove project directory after build
        ignore_mypy: ignore mypy errors
        additional_requirements_files: additional requirements files

    Returns:
        Result of build, maybe bool or container name (if docker strategy)

    """

    strategy_cont = safe(validate_ret_strategy)(strategy)

    if not is_successful(strategy_cont):
        raise strategy_cont.failure()

    strategy = strategy_cont.unwrap()

    return _dispatch(
        strategy=strategy,
        model=model,
        backend=backend,
        tag=tag,
        base_image=base_image,
        container_name=container_name,
        need_run=need_run,
        port=port,
        scan_path=scan_path,
        n_workers=n_workers,
        silent=silent,
        verbose=verbose,
        remove_project_dir=remove_project_dir,
        ignore_mypy=ignore_mypy,
        additional_requirements_files=additional_requirements_files,
    )


def _dispatch(strategy, **kwargs) -> RunResult:
    context = Context(parameters=kwargs)
    pipeline = Pipeline(context)
    if strategy == Strategy.LOCAL:
        pipeline.add(project_build)
    elif strategy == Strategy.DOCKER:
        pipeline.add(project_build)
        pipeline.add(docker_build)
    return pipeline()
