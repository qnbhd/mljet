import pytest

from deployme.utils.pipelines.pipeline import (
    Context,
    IncorrectDependsError,
    Pipeline,
)
from deployme.utils.pipelines.stage import stage


def test_pipeline_no_allow_concurrency():
    fun1 = stage("fun1")(lambda x: x + 1)
    fun2 = stage("fun2", depends_on=["fun1"])(
        lambda ctx: ctx.get_result("fun1") + 1
    )
    fun3 = stage("fun3", depends_on=["fun2"])(
        lambda ctx: ctx.get_result("fun2") ** 3
    )

    @stage("cls1", depends_on=["fun3"])
    class A:
        def __init__(self, x):
            self.x = x

        def __call__(self, ctx):
            return self.x + ctx.get_result("fun3")

    other_task = stage("other_task")(lambda some_arg: some_arg * 5)

    context = Context({"x": 1, "some_arg": 5}, {})
    pipeline = Pipeline(context)
    pipeline.add(fun1)
    pipeline.add(fun2)
    pipeline.add(fun3)
    pipeline.add(A(1))
    pipeline.add(other_task)
    pipeline()

    assert context.get_result("fun1") == 2
    assert context.get_result("fun2") == 3
    assert context.get_result("fun3") == 27
    assert context.get_result("cls1") == 28
    assert context.get_result("other_task") == 25


def test_pipeline_allow_concurrency(caplog):
    fun1 = stage("fun1")(lambda x: x + 1)
    fun2 = stage("fun2")(lambda y: y**2)

    pipeline = Pipeline(Context({"x": 1, "y": 2}, {}))

    pipeline.add(fun1)
    pipeline.add(fun2)
    pipeline(allow_isolated_concurrency=True)

    assert pipeline._context.get_result("fun1") == 2
    assert pipeline._context.get_result("fun2") == 4

    assert str(["fun1", "fun2"]) in caplog.text
    assert "parallel" in caplog.text


def test_pipeline_incorrect_depends():
    spam = stage("spam")(lambda x: x + 1)
    eggs = stage("eggs", depends_on=["spam"])(lambda x: x + 1)
    foo = stage("foo", depends_on=["bar"])(lambda x: x + 1)
    pipeline = Pipeline(Context({}, {}))
    pipeline.add(spam)
    pipeline.add(eggs)
    pipeline.add(foo)
    with pytest.raises(IncorrectDependsError):
        pipeline()
