import inspect

from deployme.utils.pipelines.stage import (
    Stage,
    stage,
)


def test_stage_runtime_checkable():

    # Classes

    @stage("A")
    class A:
        # without call
        pass

    # Not a stage
    assert not isinstance(A(), Stage)

    @stage("B")
    class B:
        # with call
        def __call__(self):
            pass

    # OK
    assert isinstance(B(), Stage)
    # Not for class, only for instances
    assert not isinstance(B, Stage)

    # dynamic
    class C:
        pass

    assert not isinstance(C(), Stage)
    assert not isinstance(C, Stage)

    c = C()
    c.name = "C"
    c.depends_on = frozenset()
    c.__call__ = lambda self, *args, **kwargs: None
    assert isinstance(c, Stage)

    # Functions
    w = 1

    def d(foo: int, bar: int, baz: int):
        """Docstring."""
        nonlocal w
        return w + foo + bar + baz

    initial_signature = inspect.signature(d)
    initial_argspec = inspect.getfullargspec(d)

    assert not isinstance(d, Stage)
    assert isinstance(stage("D")(d), Stage)

    # # initial `d` not changed
    assert not hasattr(d, "name")
    assert not hasattr(d, "depends_on")
    # # signature not changed
    assert inspect.signature(d) == initial_signature
    # argspec not changed
    assert inspect.getfullargspec(d) == initial_argspec
    # identifiers are different
    assert id(d) != id(stage("D")(d))

    # docstring is the same
    assert d.__doc__ == stage("D")(d).__doc__

    # wrapped functions can also be called as usual
    assert d(1, 2, 3) == stage("D")(d)(1, 2, 3)

    # absorption
    # stage('a1', ...) ○ stage('a2', ...) ○ stage('a3', ...) = stage('a1', ...)
    @stage("E")
    @stage("F")
    def e():
        pass

    assert isinstance(e, Stage)
    assert e.name == "E"
    assert e.depends_on == frozenset()
