from src.graph import Graph
from src.utils import bfs, bfs_with_parents


def test_bfs_simple():
    g = Graph()
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    dist = bfs(g, 1)
    assert dist == {1: 0, 2: 1, 3: 2}


def test_bfs_disconnected():
    g = Graph()
    g.add_edge(1, 2)
    g.add_edge(3, 4)  # отдельная компонента
    dist = bfs(g, 1)
    assert dist == {1: 0, 2: 1}


def test_bfs_single_vertex():
    g = Graph()
    g.add_edge(1, 1)
    dist = bfs(g, 1)
    assert dist == {1: 0}


def test_bfs_with_parents():
    g = Graph()
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    dist, parent = bfs_with_parents(g, 1)
    assert dist == {1: 0, 2: 1, 3: 2}
    assert parent == {1: -1, 2: 1, 3: 2}
