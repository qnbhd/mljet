from types import MethodType

from hypothesis import (
    given,
    strategies as st,
)

# noinspection PyProtectedMember
from mljet.contrib.analyzer import (
    _SUPPORTED_METHODS,
    extract_methods_names,
)


# skeleton for a model
class A:
    ...


def bind_methods(model, methods):
    for method in methods:
        setattr(
            model, method, MethodType(lambda self, *args, **kwargs: ..., model)
        )


@given(
    methods_names=st.sets(
        st.from_regex(r"[a-z_]+", fullmatch=True).filter(
            lambda x: x not in _SUPPORTED_METHODS
        )
    )
)
def test_analyzer_no_predicts(methods_names):
    model = A()
    bind_methods(model, methods_names)
    assert extract_methods_names(model) == []


@given(methods_names=st.sets(st.sampled_from(_SUPPORTED_METHODS)))
def test_analyzer_predicts(methods_names):
    model = A()
    bind_methods(model, methods_names)
    assert set(extract_methods_names(model)) == methods_names
