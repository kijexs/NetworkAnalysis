# тесты метрик
from src.analysis import (
    connected_components,
    double_sweep_diameter,
    largest_cc_size,
    sampled_diameter_and_percentile,
    snowball_diameter_percentile,
)
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


def test_double_sweep_simple():
    g = Graph()
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    g.add_edge(3, 1)  # треугольник
    cc = {1, 2, 3}
    diam, perc = double_sweep_diameter(g, cc, percentile=90)
    assert diam == 1
    assert perc == 1


def test_sample_distances():
    g = Graph()
    # 1-2-3-4
    for i in range(1, 4):
        g.add_edge(i, i + 1)
    cc = {1, 2, 3, 4}
    diam, perc = sampled_diameter_and_percentile(g, cc, sample_size=100, percentile=90)
    assert diam == 3
    assert perc <= 3


def test_snowball():
    g = Graph()
    for i in range(10):
        for j in range(i + 1, 10):
            g.add_edge(i, j)
    cc = set(range(10))
    diam, perc = snowball_diameter_percentile(g, cc, target_size=500, percentile=90)
    # в полном графе диаметр == 1
    assert diam == 1
    assert perc == 1
