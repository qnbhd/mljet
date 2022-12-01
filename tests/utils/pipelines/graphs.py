from hypothesis import (
    given,
    strategies as st,
)


def is_cyclic(graph) -> bool:
    """Return True if the directed graph has a cycle.
    graph must be represented as a dictionary mapping vertices to
    iterables of neighbouring vertice.
    """

    if not graph:
        return False

    path = set()

    def visit(vertex):
        path.add(vertex)
        for neighbour in graph.get(vertex, []):
            if neighbour in path or visit(neighbour):
                return True
        path.remove(vertex)
        return False

    return any(visit(v) for v in graph)


def is_topsorted(graph, order) -> bool:
    visited = set()
    if len(order) != len(graph):
        return False
    for vertex in order:
        if vertex in visited:
            return False
        visited.add(vertex)
        for neighbour in graph[vertex]:
            if neighbour in visited:
                return False
    return True


def dirgraphs(data, acyclic=False, cyclic=False, min_size=0, max_size=10):
    if acyclic and cyclic:
        raise ValueError("Cannot be both acyclic and cyclic")

    lists_params = dict(max_size=5)
    predicate = lambda x: True  # noqa: E731

    if acyclic:
        predicate = lambda x: not is_cyclic(x)  # noqa: E731
    elif cyclic:
        lists_params = dict(min_size=2, max_size=5)
        predicate = is_cyclic  # noqa: E731

    return st.dictionaries(
        st.integers(),
        st.lists(data, **lists_params),
        min_size=min_size,
        max_size=max_size,
    ).filter(predicate)
