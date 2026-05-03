# исследование устойчивости для всех графов
import os

from experiments.plot_results import plot_robustness
from src.graph import Graph
from src.robustness import degree_based_removal, evaluate_robustness, random_removal


# определение directed из пути файла
def load_graph(filepath: str) -> Graph:
    norm = os.path.normpath(filepath)
    directed = "directed" in norm.split(os.sep)
    return Graph.from_file(filepath, directed=directed)


# сбор всех файлов из datasets/
dataset_root = "datasets"
all_files = []
for dirpath, _, filenames in os.walk(dataset_root):
    for fname in filenames:
        all_files.append(os.path.join(dirpath, fname))

percentages = list(range(0, 101, 10))

for filepath in all_files:
    name = os.path.relpath(filepath, dataset_root).replace("/", "_").replace(".", "_")
    print(f"\n===== {name} =====")
    g = load_graph(filepath)

    # если граф слишком большой, можем пока пропустить устойчивость
    n = g.number_of_nodes()
    if n > 500_000:
        print(f"  Граф слишком большой ({n} вершин), устойчивость не вычисляется")
        continue

    # случайное удаление
    print("  Случайное удаление...")
    rand_res = evaluate_robustness(g, percentages, random_removal)
    # удаление по степени
    print("  Удаление по наибольшей степени...")
    deg_res = evaluate_robustness(g, percentages, degree_based_removal)

    # строим и сохраняем график
    plot_robustness(rand_res, deg_res, name=name, output_dir="results")
    print(f"  График сохранён как results/robustness_{name}.png")
