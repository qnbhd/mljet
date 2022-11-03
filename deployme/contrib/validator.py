"""Module, that contains validators for deployme."""

from pathlib import Path
from typing import (
    Optional,
    Union,
)

from returns.io import (
    IO,
    impure,
)
from returns.result import (
    Failure,
    Result,
    ResultE,
    Success,
    safe,
)
from returns.unsafe import unsafe_perform_io

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
from deployme.utils.requirements import PathLike

StrategyLike = Union[Strategy, str]


__all__ = [
    "validate_ret_strategy",
    "validate_ret_model",
    "validate_ret_port",
    "validate_ret_backend",
    "validate_ret_container_name",
]

_DEFAULT_BACKEND_NAME = "flask"


@safe
def _get_docker_client() -> ResultE:
    """Returns docker client."""
    # Lazy import (only if docker contrib is used)
    import docker

    return docker.from_env()


def validate_ret_strategy(
    strategy: StrategyLike,
) -> Result[Strategy, ValueError]:
    """Validates strategy and returns it if it is valid."""
    if isinstance(strategy, Strategy):
        return Success(strategy)
    normalized = strategy.upper()
    if normalized in Strategy.__members__:
        return Success(Strategy(normalized))
    return Failure(ValueError(f"Unknown strategy `{strategy}`"))


def validate_ret_model(model) -> Result[ModelType, ValueError]:
    """Validates model and returns it type if it is valid."""
    try:
        mt = ModelType.from_model(model)
        return Success(mt)
    except ValueError as exc:
        return Failure(ValueError(f"Unknown model passed: {exc}"))


def validate_ret_port(port: Optional[int]) -> ResultE[int]:
    """Validates port and returns it if it is valid."""
    if port is None:
        free: IO[int] = impure(find_free_port)()
        return Success(unsafe_perform_io(free))
    if port < 0 or port > 65535:
        return Failure(ValueError(f"Port `{port}` is not valid"))
    if unsafe_perform_io(impure(is_port_in_use)(port)):
        return Failure(ValueError(f"Port `{port}` is already in use"))
    return Success(port)


def validate_ret_backend(
    backend: Optional[Union[str, PathLike]]
) -> ResultE[Path]:
    """Validates backend and returns it if it is valid."""
    if not backend:
        return Success(
            dispatch_default_backend(  # type: ignore
                _DEFAULT_BACKEND_NAME, strict=True
            )
        )
    result = dispatch_default_backend(backend)
    if result:
        return Success(result)
    backend = Path(backend)
    if backend.exists() and backend.is_dir():
        return Success(backend)
    return Failure(ValueError(f"Backend `{backend}` is not found"))


def validate_ret_container_name(name: Optional[str]) -> ResultE[str]:
    """Validates container name and returns it if it is valid."""
    # if container with such name exists, then it is invalid
    import docker.errors

    if name is None:
        return Success("")
    return (
        # take docker client
        _get_docker_client()
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
