# тесты класса графов
from src.graph import Graph


def test_add_edge_undirected():
    g = Graph(directed=False)
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    assert g.number_of_nodes() == 3
    assert g.number_of_edges() == 2
    assert g.has_edge(1, 2)
    assert g.has_edge(2, 1)  # неориентированный
    assert g.degree(2) == 2


def test_add_edge_directed():
    g = Graph(directed=True)
    g.add_edge(1, 2)
    assert g.number_of_nodes() == 2
    assert g.number_of_edges() == 1
    assert g.has_edge(1, 2)
    assert not g.has_edge(2, 1)


def test_from_file_undirected(tmp_path):
    file = tmp_path / "test.edges"
    file.write_text("1 2\n2 3\n3 1\n")
    g = Graph.from_file(str(file), directed=False)
    assert g.number_of_nodes() == 3
    assert g.number_of_edges() == 3  # треугольник


def test_no_self_loops():
    g = Graph()
    g.add_edge(5, 5)
    assert g.number_of_edges() == 0
