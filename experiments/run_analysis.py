# расчет всеех метрик (1 часть задания)
import os

from experiments.plot_results import plot_degree_distribution
from src.analysis import (
    average_clustering_coefficient,
    connected_components,
    count_triangles,
    degree_distribution,
    degree_stats,
    double_sweep_diameter,
    global_clustering_coefficient,
    largest_cc_size,
    largest_cc_vertices,
    sampled_diameter_and_percentile,
    snowball_diameter_percentile,
)
from src.graph import Graph


# определение directed из пути файла
def load_graph(filepath: str) -> Graph:
    norm = os.path.normpath(filepath)
    directed = "directed" in norm.split(os.sep)
    return Graph.from_file(filepath, directed=directed)


# список файлов из datasets/
dataset_root = "datasets"
all_files = []
for dirpath, _, filenames in os.walk(dataset_root):
    for fname in filenames:
        all_files.append(os.path.join(dirpath, fname))

for filepath in all_files:
    name = os.path.relpath(filepath, dataset_root).replace("/", "_").replace(".", "_")
    print(f"\n===== {name} =====")
    g = load_graph(filepath)

    # базовые характеристики
    n = g.number_of_nodes()
    m = g.number_of_edges()
    max_edges = n * (n - 1) // 2
    dens = m / max_edges if max_edges > 0 else 0.0
    comps = connected_components(g)
    num_comps = len(comps)
    lcc_size, lcc_frac = largest_cc_size(g)

    print(f"  Вершин: {n}, Рёбер: {m}")
    print(f"  Плотность: {dens:.6f}")
    print(f"  Компонент слабой связности: {num_comps}")
    print(f"  Доля вершин в макс. компоненте: {lcc_frac:.4f}")

    # если граф ориентированный здесь нужно считать компоненты сильной связности,
    # но пока реализация только для неориентированного. потом надо не забыть добавить!!

    # оценка диаметра и 90-го процентиля
    lcc_verts = largest_cc_vertices(g)
    dbl_diam, dbl_perc = double_sweep_diameter(g, lcc_verts, percentile=90)
    smp_diam, smp_perc = sampled_diameter_and_percentile(
        g, lcc_verts, sample_size=500, percentile=90
    )
    snb_diam, snb_perc = snowball_diameter_percentile(g, lcc_verts, target_size=500, percentile=90)

    print("  Диаметр / 90-й процентиль:")
    print(f"    Double sweep:      diam={dbl_diam}, perc90={dbl_perc}")
    print(f"    Случайные пары:    diam={smp_diam}, perc90={smp_perc}")
    print(f"    Snowball sample:   diam={snb_diam}, perc90={snb_perc}")

    # треугольники и кластерные коэффициенты
    tri = count_triangles(g)
    avg_cl = average_clustering_coefficient(g)
    gcc = global_clustering_coefficient(g)
    print(f"  Треугольников: {tri}")
    print(f"  Средний кластерный коэффициент: {avg_cl:.6f}")
    print(f"  Глобальный кластерный коэффициент: {gcc:.6f}")

    # степени и распределение
    min_d, max_d, avg_d = degree_stats(g)
    print("  Степени:")
    print(f"  Минимальная: {min_d}")
    print(f"  Максимальная: {max_d}")
    print(f"  Средняя: {avg_d:.2f}")

    # построить график распределения степеней
    dist = degree_distribution(g)
    plot_degree_distribution(dist, name, output_dir="results")
