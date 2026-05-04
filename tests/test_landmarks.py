import random

from src.graph import Graph
from src.landmarks import (
    LandmarksBasic,
    LandmarksSC,
    ShortestPathTree,
    select_best_coverage_landmarks,
    select_degree_landmarks,
    select_random_landmarks,
)


# LandmarksBasic
def test_landmarks_basic_path():
    # путь 1-2-3-4, ориентир = 1, оценка расстояния 2-4 = 1+3=4
    g = Graph()
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    g.add_edge(3, 4)
    lb = LandmarksBasic(g, [1])
    est = lb.estimate(2, 4)
    assert est == 4  # верхняя граница


def test_landmarks_basic_triangle_exact():
    # треугольник: ориентиры 1 и 2, оценка для 1-3 должна быть 1
    g = Graph()
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    g.add_edge(3, 1)
    lb = LandmarksBasic(g, [1, 2])
    est = lb.estimate(1, 3)
    assert est == 1


def test_landmarks_basic_unreachable():
    # граф из двух компонент: вершины в разных компонентах дают -1
    g = Graph()
    g.add_edge(1, 2)
    g.add_edge(3, 4)
    lb = LandmarksBasic(g, [1])
    est = lb.estimate(1, 3)
    assert est == -1.0


def test_landmarks_basic_batch():
    g = Graph()
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    lb = LandmarksBasic(g, [1])
    results = lb.estimate_batch([(1, 3), (2, 3)])
    assert results == [2, 3]


# ShortestPathTree
def test_spt_parent_after_bfs():
    # корень 1, 1-2,1-3: родители 2->1,3->1
    g = Graph()
    g.add_edge(1, 2)
    g.add_edge(1, 3)
    spt = ShortestPathTree(g, 1)
    assert spt.parent[2] == 1
    assert spt.parent[3] == 1
    assert spt.parent[1] == -1


def test_spt_lca_siblings():
    # LCA 2 и 3 в звезде - 1
    g = Graph()
    g.add_edge(1, 2)
    g.add_edge(1, 3)
    spt = ShortestPathTree(g, 1)
    assert spt.lca(2, 3) == 1


def test_spt_lca_self():
    # LCA вершины с собой - она же
    g = Graph()
    g.add_edge(1, 2)
    spt = ShortestPathTree(g, 1)
    assert spt.lca(2, 2) == 2


def test_spt_lca_ancestor():
    # LCA вершины и её предка - предок
    g = Graph()
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    spt = ShortestPathTree(g, 1)
    assert spt.lca(1, 3) == 1
    assert spt.lca(3, 1) == 1


def test_distance_sc_base_no_shortcut():
    # граф: 1-2, 1-3. SPT от 1: 2->1,3->1.
    # distance_sc(2,3) = d(2,1)+d(3,1)=2
    g = Graph()
    g.add_edge(1, 2)
    g.add_edge(1, 3)
    spt = ShortestPathTree(g, 1)
    est = spt.distance_sc(2, 3)
    assert est == 2


def test_distance_sc_with_shortcut():
    # ромб: 0-1,0-2,1-3,2-3. SPT от 0: 1->0,2->0,3->1.
    # между 3 и 2 есть ребро. distance_sc(3,2) должна найти путь длиной 1.
    g = Graph()
    g.add_edge(0, 1)
    g.add_edge(0, 2)
    g.add_edge(1, 3)
    g.add_edge(2, 3)
    spt = ShortestPathTree(g, 0)
    # истинное расстояние 3-2 = 1
    est = spt.distance_sc(3, 2)
    assert est == 1


def test_distance_sc_unreachable_node():
    g = Graph()
    g.add_edge(1, 2)
    spt = ShortestPathTree(g, 1)
    est = spt.distance_sc(1, 99)  # вершина 99 не в графе
    assert est == float("inf")


# LandmarksSC
def test_landmarks_sc_two_landmarks():
    # два ориентира: 0 и 5, граф: 0-1-2-3-4-5
    # оценка расстояния 1-4: точное значение 3, т. к. путь лежит в SPT ориентира 0
    g = Graph()
    for i in range(5):
        g.add_edge(i, i + 1)
    lsc = LandmarksSC(g, [0, 5])
    est = lsc.estimate(1, 4)
    assert est == 3


def test_landmarks_sc_exact_through_lm():
    # треугольник 1-2-3 ориентир 1. estimate(2,3) = distance_sc через дерево 1
    # в дереве 1-2,1-3, shortcut 2-3 даёт точное 1
    g = Graph()
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    g.add_edge(3, 1)
    lsc = LandmarksSC(g, [1])
    est = lsc.estimate(2, 3)
    assert est == 1


# стратегии выбора ориентиров
def test_random_landmarks_count():
    g = Graph()
    for i in range(10):
        g.add_edge(i, i + 1)
    landmarks = select_random_landmarks(g, 3)
    assert len(landmarks) == 3
    assert all(0 <= lm <= 10 for lm in landmarks)


def test_degree_landmarks_order():
    g = Graph()
    g.add_edge(1, 2)
    g.add_edge(1, 3)
    g.add_edge(1, 4)  # степень 1 = 3
    g.add_edge(2, 3)  # степени 2 и 3 по 2
    landmarks = select_degree_landmarks(g, 2)
    assert landmarks[0] == 1
    assert len(landmarks) == 2


def test_coverage_landmarks_count():
    g = Graph()
    for i in range(5):
        g.add_edge(i, i + 1)
    landmarks = select_best_coverage_landmarks(g, k=2, M=100)
    assert len(landmarks) == 2
    # все вершины из графа
    assert all(0 <= lm <= 5 for lm in landmarks)


def test_coverage_landmarks_seed_reproducibility():
    g = Graph()
    g.add_edge(0, 1)
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    random.seed(42)
    lm1 = select_best_coverage_landmarks(g, k=2, M=50)
    random.seed(42)
    lm2 = select_best_coverage_landmarks(g, k=2, M=50)
    assert lm1 == lm2
