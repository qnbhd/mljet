"""Module that contains the DAG implementation."""

import copy
from collections import (
    Counter as Counter_,
    defaultdict,
    deque,
)
from typing import (
    Counter,
    DefaultDict,
    Deque,
    Dict,
    Generic,
    List,
    Set,
    TypeVar,
)

__all__ = ["DirectedAcyclicGraph", "CycleExistsError"]


T = TypeVar("T")


class CycleExistsError(Exception):
    """Exception raised when a cycle is detected in the _graph"""


class DirectedAcyclicGraph(Generic[T]):
    """
    A dag (directed acyclic _graph) is a collection of elements
    with directed relations between them. This class provides
    a way to add elements and their relations, and then _topsort
    them in a way that respects the relations.

    Example:

        >>> dag = DirectedAcyclicGraph()
        >>> dag.add("a", "b", "c")
        >>> dag.add("b", "c")
        >>> dag.add("c")
        >>> dag.add("d", "a")
        >>> dag.add("e", "d")
        >>> dag.ordered
        ['e', 'd', 'a', 'b', 'c']

    .. note::

        If a cycle is detected, the _graph will not be modified.

    .. note::

        Nodes with no incoming links will additionally be sorted
        (in `_topsort` method) by the number of outgoing links
        in descending order (i.e. nodes with more outgoing links
        will be sorted first).

    """

    def __init__(self):
        """Initialize the DAG"""
        self._graph: DefaultDict[T, List[T]] = defaultdict(list)
        self._ordered: List[T] = []

    @property
    def ordered(self) -> List[T]:
        """Returns the topologically sorted list of nodes"""
        return self._ordered[:]

    @property
    def isolated(self) -> List[T]:
        """Returns a list of isolated nodes"""
        relationscountmap = self.relationscountmap()
        return [x for x in self._graph.keys() if relationscountmap[x] == 0]

    def relationscountmap(self) -> Counter[T]:
        """Returns a map of the number of relations each node has"""
        return Counter_(x for y in self._graph.values() for x in y)

    def _topsort(self) -> List[T]:
        """
        Topologically sort the nodes in the _graph with
        additional sorting by the number of outgoing links
        (nodes with more outgoing links will be sorted first).

        Returns:
            A list of nodes in topological order

        """

        relationscountmap = self.relationscountmap()
        to_visit: Deque[T] = deque()

        to_visit.extend(
            # nodes that do not have incoming connections will
            # be added to the visit list first
            sorted(
                [x for x in self._graph.keys() if relationscountmap[x] == 0],
                # sort by the number of outgoing links
                key=lambda x: len(self._graph[x]),
                reverse=True,
            )
        )

        visited: List[T] = []
        while to_visit:
            node = to_visit.popleft()
            # select all nodes that have a relation to the current node
            # and remove the relation
            for adj in self._graph[node]:
                relationscountmap[adj] -= 1
                # if the node has no more incoming relations, add it to the
                # visit list
                if relationscountmap[adj] == 0:
                    to_visit.append(adj)
            visited.append(node)

        return visited

    def add(self, item: T, *to: T):
        """
        Add an item to the _graph, and optionally add relations to other items

        Args:
            item: The item to add
            *to: The items to add relations to

        Returns:
            None

        Raises:
            CycleExistsError: If a cycle is detected in the _graph

        .. note::
            If the item already exists in the _graph, the relations will be added
            to the existing item.

        """

        commit = copy.deepcopy(self._graph)
        self._graph[item].extend(to)
        topsorted = self._topsort()
        if len(topsorted) != len(self._graph):
            # rollback
            self._graph = commit
            raise CycleExistsError(f"Cycle detected with `{item}` and `{to}`")

        self._ordered = topsorted

    def __len__(self):
        return len(self._graph)

    def __repr__(self):
        return f"DirectedAcyclicGraph({dict(self._graph)})"

    def __contains__(self, item):
        return item in self._graph

    @classmethod
    def from_dict(cls, d: Dict[T, List[T]]) -> "DirectedAcyclicGraph[T]":
        """Create a DAG from a dictionary"""
        dag = cls()
        for item, to in d.items():
            dag.add(item, *to)
        return dag

    def edges_to(self, to: T) -> Set[T]:
        """Returns a set of vertices from which edges go to the given vertex"""
        return {x for x in self._graph.keys() if to in self._graph[x]}

    def edges_from(self, from_: T) -> Set[T]:
        """Returns a set of vertices to which edges go from the given vertex"""
        return set(self._graph[from_])
