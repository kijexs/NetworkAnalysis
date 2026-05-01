# метрики (1 часть задания)
from src.utils import bfs
from src.graph import Graph

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

def sample_distances(graph, cc_vertices, sample_size=500):
    """
    Вычисляет расстояния между случайными парами вершин.
    Возвращает список расстояний.
    """
    vertices = list(cc_vertices)
    if len(vertices) < 2:
        return []
    pairs = random.choices(vertices, k=2*sample_size)
    distances = []
    for i in range(sample_size):
        u = pairs[2*i]
        v = pairs[2*i+1]
        if u == v:
            continue
        dist = bfs(graph, u)
        if v in dist:
            distances.append(dist[v])
    return distances

def sampled_diameter_and_percentile(graph, cc_vertices, sample_size=500, percentile=90):
    """
    Возвращает (оценка диаметра, заданный процентиль)
    """
    dists = sample_distances(graph, cc_vertices, sample_size)
    if not dists:
        return 0, 0
    dists.sort()
    return max(dists), compute_percentile(dists, percentile)

def snowball_sample(graph, cc_vertices, target_size=500):
    """
    Построение подграфа методом снежного кома.
    Возвращает множество вершин подграфа.
    """
    if not cc_vertices:
        return set()
    vertices_list = list(cc_vertices)
    # случайная вершина и один её сосед
    start = random.choice(vertices_list)
    neighbors = list(graph.neighbors(start))
    if not neighbors:
        seed = {start}
    else:
        second = random.choice(neighbors)
        seed = {start, second}

    current = set(seed)
    while len(current) < target_size:
        # все соседи текущего множества, которых ещё нет в current
        frontier = set()
        for u in current:
            for v in graph.neighbors(u):
                if v not in current:
                    frontier.add(v)
        if not frontier:
            break
        current.update(frontier)

    return current

def create_subgraph(original_graph, vertices):
    """
    Создаёт новый граф с данным множеством вершин
    """
    sub = Graph(directed=original_graph.directed)
    for u in vertices:
        for v in original_graph.neighbors(u):
            if v in vertices:
                if sub.directed:
                    sub.add_edge(u, v)
                else:
                    if u < v and not sub.has_edge(u, v):
                        sub.add_edge(u, v)
    return sub

def snowball_diameter_percentile(graph, cc_vertices, target_size=500, percentile=90):
    """
    Оценка диаметра и процентиля по подграфу
    """
    sub_vertices = snowball_sample(graph, cc_vertices, target_size)
    # строим подграф и берём его макс. компоненту
    sub = create_subgraph(graph, sub_vertices)
    sub_cc = largest_cc_vertices(sub)
    if not sub_cc:
        return 0, 0
    return double_sweep_diameter(sub, sub_cc, percentile)
