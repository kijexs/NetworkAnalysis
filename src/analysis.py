# метрики (1 часть задания)
import random
from collections import defaultdict

from src.graph import Graph
from src.utils import bfs


def connected_components(graph):
    """
    Возвращает список компонент слабой связности.
    Каждая компонента - множество вершин.
    """
    visited = set()
    components = []

    for node in graph.nodes():
        if node in visited:
            continue
        dist = bfs(graph, node)  # возвращает {вершина: расстояние}
        comp = set(dist)  # множество достижимых вершин
        visited.update(comp)
        components.append(comp)

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
    return max(comp, key=len)  # компонента с максимумом вершин


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
    pairs = random.choices(vertices, k=2 * sample_size)
    distances = []
    for i in range(sample_size):
        u = pairs[2 * i]
        v = pairs[2 * i + 1]
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


def count_triangles(graph):
    """
    Подсчет числа треугольников
    путем сортировки ребер по степеням
    """
    triangles = 0
    # для каждой вершины ищем соседей у который степень больше
    # или при равных степ. номер больше
    for u in graph.nodes():
        deg_u = graph.degree(u)
        larger_neighbors = []
        for v in graph.neighbors(u):
            deg_v = graph.degree(v)
            if deg_v > deg_u or (deg_v == deg_u and v > u):
                larger_neighbors.append(v)
        for i in range(len(larger_neighbors)):
            v = larger_neighbors[i]
            for j in range(i + 1, len(larger_neighbors)):
                w = larger_neighbors[j]
                if graph.has_edge(v, w):
                    triangles += 1
    return triangles


def average_clustering_coefficient(graph, vertices=None):
    """
    Считает средний кластерный коэффициент
    """
    count = 0
    total_cl_u = 0.0
    # если не заданы работаем со всем графом
    if vertices is None:
        vertices = graph.nodes()
    for u in vertices:
        neighbors = graph.neighbors(u)
        k = len(neighbors)
        if k < 2:
            cl_u = 0.0
        else:
            edges = 0
            neigh_list = list(neighbors)
            for i in range(len(neigh_list)):
                v = neigh_list[i]
                for j in range(i + 1, len(neigh_list)):
                    w = neigh_list[j]
                    if graph.has_edge(v, w):
                        edges += 1
            cl_u = 2 * edges / (k * (k - 1))
        total_cl_u += cl_u
        count += 1
    return total_cl_u / count if count > 0 else 0.0


def global_clustering_coefficient(graph):
    """
    Считает глобальный кластерный коэффициент
    = число закрытых троек / число всех троек
    """
    triangles = count_triangles(graph)
    triples = 0
    for u in graph.nodes():
        k = graph.degree(u)
        triples += k * (k - 1) // 2
    if triples == 0:
        return 0.0
    return triangles * 3.0 / triples


def degree_stats(graph):
    """
    Возвращает (min_degree, max_degree, avg_degree) для графа
    """
    degrees = [graph.degree(u) for u in graph.nodes()]
    if not degrees:
        return 0, 0, 0.0
    min_deg = min(degrees)
    max_deg = max(degrees)
    avg_deg = sum(degrees) / len(degrees)
    return min_deg, max_deg, avg_deg


def degree_distribution(graph):
    """
    Возвращает словарь {степень: доля вершин с такой степенью}.
    Сумма долей равна 1.0.
    """
    n = graph.number_of_nodes()
    if n == 0:
        return {}
    # подсчитываем частоту каждой степени
    degree_counts = defaultdict(int)
    for u in graph.nodes():
        degree_counts[graph.degree(u)] += 1
    # переводим в доли
    dist = {d: count / n for d, count in degree_counts.items()}
    return dist
