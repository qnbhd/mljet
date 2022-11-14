"""Module contains type's aliases."""

import pathlib
from typing import (
    IO,
    Any,
    Protocol,
    Union,
    final,
    runtime_checkable,
)

PathLike = Union[str, pathlib.Path]


@runtime_checkable
@final
class Serializer(Protocol):
    """Protocol for serializers."""

    @staticmethod
    def dump(obj: Any, file: IO, *args, **kwargs) -> None:
        ...

    @staticmethod
    def load(file: IO, *args, **kwargs) -> Any:
        ...


@runtime_checkable
@final
class Estimator(Protocol):
    """Protocol for estimators."""

    def fit(self, *args, **kwargs) -> Any:
        ...

    def predict(self, *args, **kwargs) -> Any:
        ...
