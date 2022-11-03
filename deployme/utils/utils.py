"""Utils module."""
import inspect


def drop_unnecessary_kwargs(func, kwargs):
    """Drop unnecessary kwargs."""
    spec = inspect.getfullargspec(func).args
    return {arg: value for arg, value in kwargs.items() if arg in spec}
