# тесты метрик
from src.analysis import connected_components, largest_cc_size
from src.graph import Graph


def test_connected_components_one():
    g = Graph()
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    comp = connected_components(g)
    assert len(comp) == 1
    assert comp[0] == {1, 2, 3}


def test_connected_components_two():
    g = Graph()
    g.add_edge(1, 2)
    g.add_edge(3, 4)
    comp = connected_components(g)
    assert len(comp) == 2
    assert comp[0] == {1, 2}
    assert comp[1] == {3, 4}


def test_largest_cc():
    g = Graph()
    g.add_edge(1, 2)
    g.add_edge(3, 4)
    g.add_edge(4, 5)
    size, frac = largest_cc_size(g)
    assert size == 3
    assert frac == 3 / 5
