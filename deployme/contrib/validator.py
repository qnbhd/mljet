"""Module, that contains validators for deployme."""

import re
from pathlib import Path
from typing import (
    Optional,
    Union,
)

from returns.pipeline import is_successful
from returns.result import (
    Failure,
    Success,
    safe,
)

from deployme.contrib.supported import (
    ModelType,
    Strategy,
)
from deployme.cookie.templates.backends.dispatcher import (
    dispatch_default_backend,
)
from deployme.utils.conn import (
    find_free_port,
    is_port_in_use,
)
from deployme.utils.types import (
    Estimator,
    PathLike,
)

StrategyLike = Union[Strategy, str]


__all__ = [
    "validate_ret_strategy",
    "validate_ret_model",
    "validate_ret_port",
    "validate_ret_backend",
    "validate_ret_container_name",
]

_DEFAULT_BACKEND_NAME = "flask"


def _get_docker_client():
    """Returns docker client."""
    # Lazy import (only if docker contrib is used)
    import docker

    return docker.from_env()


def validate_ret_strategy(
    strategy: StrategyLike,
) -> Strategy:
    """Validates strategy and returns it if it is valid."""
    if isinstance(strategy, Strategy):
        return strategy
    normalized = strategy.upper()
    if normalized in Strategy.__members__:
        return Strategy(normalized)
    raise ValueError(f"Unknown strategy `{strategy}`")


def validate_ret_model(model: Estimator) -> ModelType:
    """Validates model and returns it type if it is valid."""
    try:
        mt = ModelType.from_model(model)
        return mt
    except ValueError as exc:
        raise ValueError(f"Unknown model passed: {exc}")


def validate_ret_port(port: Optional[int]) -> int:
    """Validates port and returns it if it is valid."""
    if port is None:
        return find_free_port()
    if port < 0 or port > 65535:
        raise ValueError(f"Port `{port}` is not valid")
    if is_port_in_use(port):
        raise ValueError(f"Port `{port}` is already in use")
    return port


def validate_ret_backend(backend: Optional[Union[str, PathLike]]) -> Path:
    """Validates predefined backend name or path to custom backend."""
    if backend is None:
        return dispatch_default_backend(_DEFAULT_BACKEND_NAME, strict=True)  # type: ignore
    backend_disp_result = dispatch_default_backend(backend)
    if backend_disp_result:
        return backend_disp_result
    backend = Path(backend)
    if backend.exists() and backend.is_dir():
        return backend
    raise ValueError(f"Backend `{backend}` is not found")


def _check_container_name_by_regex(name: str) -> bool:
    return bool(re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]+", name))


def validate_ret_container_name(name: str) -> str:
    """Validates container name and returns it if it is valid."""
    # if container with such name exists, then it is invalid
    import docker.errors

    if not _check_container_name_by_regex(name):
        raise ValueError(f"Container name `{name}` is not valid")

    validate_cont_name_result = (
        # take docker client
        safe(_get_docker_client)()
        # attempt to get container by name
        .bind(safe(lambda client: client.containers.get(name)))  # type: ignore
        # if it is found, then it is invalid
        .bind(
            # run only if previous step was successful
            lambda x: Failure(ValueError(f"Container name `{name}` is exists"))
        )
        # handle Failure from previous steps
        .lash(
            lambda x: (
                # only if docker.errors.NotFound is raised
                Success(name)
                if isinstance(x, docker.errors.NotFound)
                # delegate other errors
                else Failure(x)
            )
        )
    )

    if not is_successful(validate_cont_name_result):
        raise validate_cont_name_result.failure()

    return validate_cont_name_result.unwrap()
