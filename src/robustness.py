import random
from typing import Callable, List, Tuple

from src.analysis import largest_cc_size_ignore


def random_removal(graph, fraction: float) -> set:
    """
    Возвращает множество случайно выбранных вершин
    заданной доли (0..1)
    """
    nodes = list(graph.nodes())
    k = max(0, min(len(nodes), int(len(nodes) * fraction)))
    return set(random.sample(nodes, k))


def degree_based_removal(graph, fraction: float) -> set:
    """
    Возвращает множество вершин с наибольшей степенью
    заданной доли
    """
    nodes = list(graph.nodes())
    k = max(0, min(len(nodes), int(len(nodes) * fraction)))
    if k == 0:
        return set()

    sorted_nodes = sorted(nodes, key=lambda v: (graph.degree(v), v), reverse=True)
    return set(sorted_nodes[:k])


def evaluate_robustness(
    graph, percentages: List[int], strategy: Callable
) -> List[Tuple[int, float]]:
    """
    Для каждого процента из списка percentages
    вычисляет долю вершин в максимальной компоненте после удаления.
    Возвращает список кортежей (процент, доля_в_МК).
    """
    results = []
    for p in percentages:
        fraction = p / 100.0
        removed = strategy(graph, fraction)
        _, lcc_frac = largest_cc_size_ignore(graph, removed)
        results.append((p, lcc_frac))
    return results
