# метрики (1 часть задания)
from src.utils import bfs

import random

def connected_components(graph):
    """
    Возвращает список компонент слабой связности.
    Каждая компонента - множество вершин.
    """
    unvisited = set(graph.nodes())
    components = []

    while unvisited:
        start = unvisited.pop()
        dist = bfs(graph, start)  # возвращает {вершина: расстояние}
        comp = set(dist.keys())  # множество достижимых вершин
        components.append(comp)
        unvisited -= comp

    return components


def largest_cc_size(graph):
    """
    Возвращает (размер максимальной компоненты,
    доля от общего числа вершин)
    """
    comp = connected_components(graph)
    if not comp:
        return 0, 0.0
    n = graph.number_of_nodes()
    max_size = max(len(c) for c in comp)
    fraction = max_size / n if n > 0 else 0.0
    return max_size, fraction

def largest_cc_vertices(graph):
    """
    Возвращает множество вершин наибольшей компоненты
    слабой связности
    """
    comp = connected_components(graph)
    if not comp:
        return set()
    return max(comp, key=len)   # компонента с максимумом вершин


def compute_percentile(sorted_list, percentile):
    """
    Возвращает значение заданного процентиля
    по отсортированному списку
    """
    if not sorted_list:
        return 0
    idx = int(len(sorted_list) * percentile / 100)
    return sorted_list[min(idx, len(sorted_list) - 1)]

def double_sweep_diameter(graph, cc_vertices=None, percentile=90):
    """
    Оценка диаметра методом double sweep.
    Если cc_vertices не передано, работает со всем графом.
    Возвращает (оценка диаметра, заданный процентиль).
    """
    vertices = cc_vertices if cc_vertices is not None else set(graph.nodes())
    if not vertices:
        return 0, 0

    # случайная стартовая вершина
    r = random.choice(list(vertices))
    dist_r = bfs(graph, r)
    a = max(dist_r, key=lambda v: dist_r[v])
    dist_a = bfs(graph, a)
    b = max(dist_a, key=lambda v: dist_a[v])
    diam = dist_a[b]
    distances = sorted(dist_a.values())

    return diam, compute_percentile(distances, percentile)

