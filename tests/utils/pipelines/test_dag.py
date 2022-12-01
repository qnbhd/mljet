import pytest
from hypothesis import (
    given,
    settings,
    strategies as st,
)

from deployme.utils.pipelines.dag import (
    CycleExistsError,
    DirectedAcyclicGraph,
)
from tests.utils.pipelines.graphs import (
    dirgraphs,
    is_cyclic,
    is_topsorted,
)


@given(
    dirgraphs(st.integers(), acyclic=True),
)
@settings(deadline=None)
def test_dag_is_acyclic(graph):
    dag = DirectedAcyclicGraph.from_dict(graph)
    assert not is_cyclic(dag._graph)


@given(
    dirgraphs(st.integers(), acyclic=True),
)
@settings(deadline=None)
def test_dag_is_topsorted(items):
    dag = DirectedAcyclicGraph.from_dict(items)
    assert is_topsorted(dag._graph, dag.ordered)


@given(
    dirgraphs(st.integers(), cyclic=True),
)
@settings(deadline=None)
def test_dag_cyclic_raises(items):
    with pytest.raises(CycleExistsError):
        DirectedAcyclicGraph.from_dict(items)


def test_dag_add_atomic():
    dag = DirectedAcyclicGraph.from_dict({1: [], 2: [1], 3: [2]})
    with pytest.raises(CycleExistsError):
        dag.add(1, 3)
        # rollback
    with pytest.raises(CycleExistsError):
        dag.add(2, 3)
        # rollback
    assert is_topsorted(dag._graph, dag.ordered)
    assert not is_cyclic(dag._graph)


@pytest.mark.repeat(10)
def test_dag():
    dag = DirectedAcyclicGraph()
    dag.add("Python")
    dag.add("C++")
    dag.add("C")
    dag.add("C", "C++")
    dag.add("Haskell")
    dag.add("C", "Python")
    dag.add("C++", "Python")
    dag.add("Haskell", "Python")

    dag.add("Guido", "Python")
    dag.add("Bjarne", "C++")
    dag.add("Dennis", "C")
    dag.add("Simon", "Haskell")

    assert dag.ordered == [
        "Guido",
        "Bjarne",
        "Dennis",
        "Simon",
        "C",
        "Haskell",
        "C++",
        "Python",
    ]

    assert dag.edges_to("Python") == {"C", "C++", "Haskell", "Guido"}
    assert dag.edges_from("Python") == set()
