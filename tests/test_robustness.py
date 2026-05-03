from src.analysis import connected_components_ignore, largest_cc_size_ignore
from src.graph import Graph
from src.robustness import degree_based_removal, evaluate_robustness, random_removal
from src.utils import bfs_ignore


def test_random_removal_size():
    g = Graph()
    for i in range(10):
        g.add_edge(i, i + 1)  # 11 вершин 0..10
    removed = random_removal(g, 0.3)
    assert len(removed) == int(11 * 0.3)
    assert removed.issubset(set(range(11)))


def test_random_removal_zero():
    g = Graph()
    g.add_edge(1, 2)
    assert random_removal(g, 0.0) == set()


def test_degree_based_removal():
    g = Graph()
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    g.add_edge(3, 4)
    g.add_edge(4, 5)
    # степени: 1:1, 2:2, 3:2, 4:2, 5:1
    removed = degree_based_removal(g, 0.4)  # 40% от 5 = 2 вершины
    assert len(removed) == 2
    # максимальная степень в графе = 2
    max_deg = max(g.degree(v) for v in g.nodes())
    for v in removed:
        assert g.degree(v) == max_deg
    # вершины со степенью меньше максимальной не должны быть удалены
    for v in g.nodes():
        if g.degree(v) < max_deg:
            assert v not in removed


def test_bfs_ignore():
    g = Graph()
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    g.add_edge(3, 4)
    # удалим вершину 3
    dist = bfs_ignore(g, 1, {3})
    assert dist == {1: 0, 2: 1}
    # старт из удалённой
    assert bfs_ignore(g, 3, {3}) == {}


def test_connected_components_ignore():
    g = Graph()
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    g.add_edge(4, 5)
    comps = connected_components_ignore(g, {2})
    # должны остаться компоненты {1}, {3}, {4,5}
    assert len(comps) == 3
    assert {1} in comps
    assert {3} in comps
    assert {4, 5} in comps


def test_largest_cc_size_ignore():
    g = Graph()
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    g.add_edge(4, 5)
    size, frac = largest_cc_size_ignore(g, {2})
    # компоненты {1}, {3}, {4,5}
    # Максимальный размер = 2, общее число вершин = 4 => доля 0.5
    assert size == 2
    assert frac == 0.5


def test_evaluate_robustness():
    g = Graph()
    for i in range(1, 6):
        g.add_edge(i, i + 1)  # путь 1-2-3-4-5-6
    # при удалении 50% случайных вершин
    # ожидаем, что доля в МК уменьшится
    res = evaluate_robustness(g, [0, 50, 100], random_removal)
    assert len(res) == 3
    # при 0% доля = 1.0
    assert res[0][1] == 1.0
    # при 100% доля = 0.0
    assert res[-1][1] == 0.0
    # при 50% доля < 1.0
    assert res[1][1] < 1.0
