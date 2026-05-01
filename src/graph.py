from collections import defaultdict
from typing import Iterable, Set, Tuple


class Graph:
    def __init__(self, directed: bool = False):
        self.adj: dict[int, set[int]] = defaultdict(set)
        self.directed = directed
        self._num_edges = 0
        self._nodes: Set[int] = set()  # множество всех уникальных вершин

    def add_edge(self, u: int, v: int) -> None:
        # могут быть петли, мы их игнорируем
        if u == v:
            return
        self._nodes.add(u)
        self._nodes.add(v)
        # добавляем связь
        if v not in self.adj[u]:
            self.adj[u].add(v)
            self._num_edges += 1
        if not self.directed:
            if u not in self.adj[v]:
                self.adj[v].add(u)

    def has_edge(self, u: int, v: int) -> bool:
        return v in self.adj.get(u, set())

    def neighbors(self, u: int) -> Set[int]:
        return self.adj.get(u, set()).copy()

    def degree(self, u: int) -> int:
        return len(self.adj.get(u, set()))

    def number_of_nodes(self) -> int:
        return len(self._nodes)

    def number_of_edges(self) -> int:
        return self._num_edges

    def nodes(self) -> Iterable[int]:
        return self._nodes

    def edges(self) -> Iterable[Tuple[int, int]]:
        seen = set()
        for u in self.adj:
            for v in self.adj[u]:
                if self.directed:
                    yield (u, v)
                else:
                    if (v, u) not in seen:
                        seen.add((u, v))
                        yield (u, v)

    @staticmethod
    def from_file(filename: str, directed: bool = False) -> "Graph":
        # читает граф из файла, где каждая строка: u v
        graph = Graph(directed)
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):  # пропускаем комментарии
                    continue
                parts = line.split()
                if len(parts) < 2:
                    continue
                try:
                    u, v = int(parts[0]), int(parts[1])
                    graph.add_edge(u, v)
                except ValueError:
                    # возможно, строка с заголовком или нечисловыми данными
                    continue
        return graph
