# метрики (1 часть задания)
from src.utils import bfs


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
