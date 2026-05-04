import random
from collections import defaultdict
from typing import Dict, List, Tuple

from src.graph import Graph
from src.utils import bfs, bfs_with_parents


class LandmarksBasic:
    """
    Базовая оценка расстояний методом ориентиров
    """

    def __init__(self, graph: Graph, landmarks: List[int]):
        self.graph = graph
        self.landmarks = landmarks
        self.dist = {}
        for lm in landmarks:
            self.dist[lm] = bfs(graph, lm)

    @classmethod
    def from_strategy(cls, graph: Graph, k: int, strategy: str = "random", **kwargs):
        """
        Создаёт экземпляр с автоматическим выбором k ориентиров.
        strategy: 'random', 'degree', 'coverage'.
        kwargs: доп параметр (M для coverage).
        """
        if strategy == "random":
            landmarks = select_random_landmarks(graph, k)
        elif strategy == "degree":
            landmarks = select_degree_landmarks(graph, k)
        elif strategy == "coverage":
            M = kwargs.get("M", 500)
            landmarks = select_best_coverage_landmarks(graph, k, M=M)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
        return cls(graph, landmarks)

    def estimate(self, u: int, v: int) -> float:
        # min u∈U (du[s] + du[t])
        best = float("inf")
        for lm in self.landmarks:
            du = self.dist[lm].get(u)
            dv = self.dist[lm].get(v)
            if du is not None and dv is not None:
                d = du + dv
                if d < best:
                    best = d
        return best if best != float("inf") else -1.0

    def estimate_batch(self, pairs: List[Tuple[int, int]]) -> List[float]:
        return [self.estimate(u, v) for u, v in pairs]


class ShortestPathTree:
    """
    Дерево кратчайших путей от одного ориентира
    """

    def __init__(self, graph: Graph, root: int):
        self.graph = graph
        self.root = root
        dist, parent = bfs_with_parents(graph, root)

        self.dist: Dict[int, int] = dist
        self.parent: Dict[int, int] = parent  # parent[root] = -1

        # подготовка структур для LCA
        self._prepare_lca()

    def _prepare_lca(self):
        """
        Препроцессинг для LCA.
        Строит массив up[v][k] - предок v на расстоянии 2^k,
        а также времена входа/выхода для проверки на предка.
        """
        nodes = list(self.dist.keys())
        n = len(nodes)

        # времена входа/выхода для проверки is_ancestor
        self.tin = {v: 0 for v in nodes}
        self.tout = {v: 0 for v in nodes}
        self.timer = 0

        # максимальная степень двойки, не превосходящая n
        self.LOG = max(1, (n.bit_length()))
        # up[k][v] - предок v на расстоянии 2^k
        # используем словари: up[k] - словарь {v: ancestor}
        self.up: List[Dict[int, int]] = [{} for _ in range(self.LOG)]

        # запускаем dfs из корня для заполнения tin/tout и up[0]
        self._dfs(self.root, -1)

        # заполняем остальные уровни up
        for k in range(1, self.LOG):
            for v in nodes:
                mid = self.up[k - 1].get(v, v)
                self.up[k][v] = self.up[k - 1].get(mid, mid)

    def _dfs(self, v: int, p: int):
        """
        Обход в глубину для заполнения tin/tout и первого уровня up
        """
        self.tin[v] = self.timer
        self.timer += 1
        self.up[0][v] = p if p != -1 else v  # родитель или сам узел (для корня)
        for child, parent_of_child in self.parent.items():
            if parent_of_child == v:
                self._dfs(child, v)
        self.tout[v] = self.timer
        self.timer += 1

    def _is_ancestor(self, a: int, b: int) -> bool:
        """
        Проверяет, является ли вершина a предком вершины b
        """
        return self.tin[a] <= self.tin[b] and self.tout[a] >= self.tout[b]

    def lca(self, u: int, v: int) -> int:
        """
        Возвращает наименьшего общего предка вершин u и v в этом дереве
        """
        if self._is_ancestor(u, v):
            return u
        if self._is_ancestor(v, u):
            return v
        # поднимаем u, пока не найдём предка v
        for k in range(self.LOG - 1, -1, -1):
            if not self._is_ancestor(self.up[k].get(u, u), v):
                u = self.up[k][u]
        return self.up[0][u]

    def _path_to_ancestor(self, v: int, ancestor: int) -> List[int]:
        """
        Возвращает список вершин на пути от v до ancestor
        """
        if v == ancestor:
            return [v]
        path = []
        cur = v
        while cur != ancestor:
            path.append(cur)
            cur = self.parent[cur]
        path.append(ancestor)
        return path

    def distance_sc(self, u: int, v: int) -> float:
        """
        Оценка расстояния между u и v (алгоритм Distance-SC)
        """
        if u not in self.dist or v not in self.dist:
            return float("inf")

        w = self.lca(u, v)
        # базовое расстояние через lca
        best = self.dist[u] + self.dist[v] - 2 * self.dist[w]

        path_u = self._path_to_ancestor(u, w)
        path_v = self._path_to_ancestor(v, w)

        for x in path_u:
            for y in path_v:
                if self.graph.has_edge(x, y):
                    cand = (self.dist[u] - self.dist[x]) + 1 + (self.dist[v] - self.dist[y])
                    if cand < best:
                        best = cand
        return best


class LandmarksSC:
    """
    Оценка расстояний через SPT и LCA
    """

    def __init__(self, graph: Graph, landmarks: List[int]):
        self.graph = graph
        self.landmarks = landmarks
        self.trees = {}
        for lm in landmarks:
            self.trees[lm] = ShortestPathTree(graph, lm)

    @classmethod
    def from_strategy(cls, graph: Graph, k: int, strategy: str = "random", **kwargs):
        if strategy == "random":
            landmarks = select_random_landmarks(graph, k)
        elif strategy == "degree":
            landmarks = select_degree_landmarks(graph, k)
        elif strategy == "coverage":
            M = kwargs.get("M", 500)
            landmarks = select_best_coverage_landmarks(graph, k, M=M)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
        return cls(graph, landmarks)

    def estimate(self, u: int, v: int) -> float:
        best = float("inf")
        for tree in self.trees.values():
            d = tree.distance_sc(u, v)
            if d < best:
                best = d
        return best if best != float("inf") else -1.0


# стратегии выбора ориентиров
def select_random_landmarks(graph: Graph, count: int) -> List[int]:
    """
    Выбрать случайные вершины без повторений
    """
    nodes = list(graph.nodes())
    if count >= len(nodes):
        return nodes
    return random.sample(nodes, count)


def select_degree_landmarks(graph: Graph, count: int) -> List[int]:
    """
    Выбрать вершины с наибольшей степенью
    """
    nodes = list(graph.nodes())
    nodes.sort(key=lambda v: graph.degree(v), reverse=True)
    return nodes[:count]


def select_best_coverage_landmarks(graph: Graph, k: int, M: int = 500, **kwargs) -> List[int]:
    """
    Выбор k ориентиров по стратегии Best-Coverage (алгоритм 4 из статьи).
    M - количество случайных пар для построения пулов кратчайших путей.
    """
    nodes = list(graph.nodes())
    N = len(nodes)
    if k >= N:
        return nodes

    # собираем все вершины, участвующие в кратчайших путях
    # и считаем счётчик покрытия для каждой вершины
    cover_count = defaultdict(int)

    # генерируем M случайных пар (s,t)
    for _ in range(M):
        s = random.choice(nodes)
        t = random.choice(nodes)
        if s == t:
            continue
        # используем bfs_with_parents, чтобы восстановить путь
        dist, parent = bfs_with_parents(graph, s)
        if t not in dist:  # недостижима
            continue
        # восстанавливаем путь от t к s
        path = []
        cur = t
        while cur != -1:
            path.append(cur)
            cur = parent[cur]
        # увеличиваем счётчик для каждой вершины пути
        for v in path:
            cover_count[v] += 1

    # отбираем k вершин с наибольшим покрытием, разрешая произвольный выбор при равных счётчиках
    sorted_vertices = sorted(cover_count.keys(), key=lambda v: (cover_count[v], v), reverse=True)
    return sorted_vertices[:k]
