"""Module that contains Stage protocol implementation."""

import types
from functools import (
    update_wrapper,
    wraps,
)
from typing import (
    Callable,
    FrozenSet,
    Iterable,
    Optional,
    Protocol,
    Type,
    TypeVar,
    Union,
    runtime_checkable,
)

__all__ = ["Stage", "stage"]


@runtime_checkable
class Stage(Protocol):
    """Stage protocol."""

    # stage name
    name: str

    # a list of the stages, or their names,
    #  on which the stage is based
    depends_on: FrozenSet[str]

    # all stage must be callable
    def __call__(self, *args, **kwargs):
        ...  # fmt: skip


StageName = str

T = TypeVar("T")
U = TypeVar("U")


def stage(name: StageName, depends_on: Optional[Iterable[StageName]] = None):
    """
    Decorator to set stage trait to the object.

    Set next attributes to the decorated object:
        - name: name of the stage
        - depends_on: a list of the stages, or their names

    Args:
        name: stage name
        depends_on: a list of the stages, or their names,
            on which the stage is based

    Returns:
        Object with `Stage` trait.

    """

    def decorator(obj: Union[Callable[..., T], Type[U]]):

        if isinstance(obj, type):
            # if the object is a class, we need to create a new class
            #  that inherits from the original class and implements
            #  the `Stage` protocol

            # NOTE: we need to create a new class, because we want
            #   to use the original class without `Stage` protocol
            #   traits, and we can't do that if we modify the original
            #   class

            cls: Type[U] = obj

            stage_name = name

            @wraps(cls, updated=())
            class StageClass(cls):  # type: ignore
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.name = stage_name
                    self.depends_on = frozenset(depends_on or [])

            return StageClass

        # if the object is a function, we need to create a new function
        #  that wraps the original function and implements the Stage protocol

        # NOTE: we need to create a new function, because we want
        #   to use the original function without Stage protocol
        #   traits, and we can't do that if we modify the original
        #   function

        callee: Callable[..., T] = obj

        # noinspection PyUnresolvedReferences
        stage_func = types.FunctionType(
            obj.__code__,
            obj.__globals__,
            name=obj.__name__,
            argdefs=obj.__defaults__,
            closure=obj.__closure__,
        )
        stage_func = update_wrapper(stage_func, callee)
        stage_func.__kwdefaults__ = stage.__kwdefaults__
        # set up the stage protocol traits
        stage_func.name = name  # type: ignore
        stage_func.depends_on = frozenset(depends_on or [])  # type: ignore

        return stage_func

    return decorator
