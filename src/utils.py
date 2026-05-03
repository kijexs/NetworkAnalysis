# bfs, вспомогательные функции и тд
from collections import deque
from typing import Dict, Tuple


def bfs(graph, start: int) -> Dict[int, int]:
    """
    Поиск в ширину от вершины start.
    Возвращает словарь {вершина: расстояние} для всех вершин,
    достижимых из start.
    """
    # словарь расстояний
    dist: Dict[int, int] = {start: 0}

    queue = deque([start])
    adj = graph.adj
    while queue:
        current = queue.popleft()
        # текущее расстояние до current
        d = dist[current]
        # перебираем всех соседей current
        for neighbor in adj.get(current, ()):
            if neighbor not in dist:
                dist[neighbor] = d + 1
                queue.append(neighbor)

    return dist


def bfs_ignore(graph, start: int, ignore: set) -> Dict[int, int]:
    """
    bfs, который пропускает вершины из множества ignore и не заходит в них.
    Возвращает словарь расстояний только для неигнорируемых вершин.
    """
    if start in ignore:
        return {}

    dist: Dict[int, int] = {start: 0}

    queue = deque([start])
    adj = graph.adj
    while queue:
        current = queue.popleft()
        d = dist[current]
        for neighbor in adj.get(current, ()):
            if neighbor not in ignore and neighbor not in dist:
                dist[neighbor] = d + 1
                queue.append(neighbor)

    return dist


def bfs_with_parents(graph, start: int) -> Tuple[Dict[int, int], Dict[int, int]]:
    """
    Возвращает (dist, parent) - словари расстояний и родителей.
    parent[v] - предшественник v на кратчайшем пути от start.
    Для start parent[start] = -1.
    """
    dist: Dict[int, int] = {start: 0}

    parent = {start: -1}
    queue = deque([start])
    adj = graph.adj
    while queue:
        current = queue.popleft()
        d = dist[current]
        for neighbor in adj.get(current, ()):
            if neighbor not in dist:
                dist[neighbor] = d + 1
                parent[neighbor] = current
                queue.append(neighbor)

    return dist, parent
