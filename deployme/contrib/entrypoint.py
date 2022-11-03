"""Docker builder module."""

import logging
from typing import (
    Optional,
    Union,
)

from returns.pipeline import is_successful

from deployme.contrib.docker_.runner import docker as docker_runner
from deployme.contrib.local import local as local_runner
from deployme.contrib.supported import Strategy
from deployme.contrib.validator import validate_ret_strategy
from deployme.utils.requirements import PathLike
from deployme.utils.utils import drop_unnecessary_kwargs

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
    port: int = 5000,
    scan_path: Optional[PathLike] = None,
    n_workers: int = 1,
    silent: bool = True,
    verbose: bool = False,
    remove_project_dir: bool = False,
):
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

    Returns:
        ...

    """

    strategy_cont = validate_ret_strategy(strategy)

    if not is_successful(strategy_cont):
        raise strategy_cont.failure()

    strategy = strategy_cont.unwrap()

    return dispatch(
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
    )


def dispatch(strategy, **kwargs):
    if strategy == Strategy.DOCKER:
        return docker_runner(**drop_unnecessary_kwargs(docker_runner, kwargs))
    if strategy == Strategy.LOCAL:
        return local_runner(**drop_unnecessary_kwargs(local_runner, kwargs))
    raise ValueError(f"Strategy {strategy} is not supported")
