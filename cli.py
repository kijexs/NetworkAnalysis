from src.graph import Graph
from src.analysis import (
    connected_components, largest_cc_size, largest_cc_vertices,
    double_sweep_diameter,
    sampled_diameter_and_percentile,
    snowball_diameter_percentile,
    count_triangles,
    average_clustering_coefficient,
    global_clustering_coefficient,
    degree_stats,
)
from src.utils import bfs

def load_graph_interactive():
    path = input("Введите путь к файлу графа: ").strip()
    directed = 'directed' in path.lower()
    return Graph.from_file(path, directed=directed)

def print_metrics(g):
    print("\n--- Основные характеристики ---")
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
    if g.directed:
        print("пока не реализовано")

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

    print("\n--- Треугольники и кластерные коэффициенты ---")
    tri = count_triangles(g)
    avg_cl = average_clustering_coefficient(g)
    gcc = global_clustering_coefficient(g)
    print(f"  Треугольников: {tri}")
    print(f"  Средний кластерный коэффициент: {avg_cl:.6f}")
    print(f"  Глобальный кластерный коэффициент: {gcc:.6f}")

    min_d, max_d, avg_d = degree_stats(g)
    print(f"\n--- Степени ---")
    print(f"  Минимальная: {min_d}")
    print(f"  Максимальная: {max_d}")
    print(f"  Средняя: {avg_d:.2f}")

def compute_distance(g):
    try:
        u = int(input("Введите вершину u: "))
        v = int(input("Введите вершину v: "))
    except ValueError:
        print("Некорректный ввод")
        return
    dist = bfs(g, u)
    if v in dist:
        print(f"Кратчайшее расстояние между {u} и {v}: {dist[v]}")
    else:
        print(f"Пути между {u} и {v} не существует")

def compute_local_clustering(g):
    try:
        u = int(input("Введите вершину: "))
    except ValueError:
        print("Некорректный ввод")
        return
    neighbors = g.neighbors(u)
    k = len(neighbors)
    if k < 2:
        print(f"Локальный кластерный коэффициент для {u} = 0")
        return
    links = 0
    neigh_list = list(neighbors)
    for i in range(len(neigh_list)):
        for j in range(i+1, len(neigh_list)):
            if g.has_edge(neigh_list[i], neigh_list[j]):
                links += 1
    cl = (2.0 * links) / (k * (k - 1))
    print(f"Локальный кластерный коэффициент для {u} = {cl:.6f}")

def main():
    print("Загружайте граф и исследуйте его характеристики.\n")
    g = None
    while True:
        print("\n===== Меню =====")
        print("1. Загрузить граф")
        print("2. Показать все метрики")
        print("3. Расстояние между двумя вершинами")
        print("4. Локальный кластерный коэффициент вершины")
        print("5. Симуляция удаления узлов")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()
        if choice == "1":
            g = load_graph_interactive()
            print("Граф загружен")
        elif choice == "2":
            if g is None:
                print("Сначала загрузите граф (пункт 1)")
            else:
                print_metrics(g)
        elif choice == "3":
            if g is None:
                print("Сначала загрузите граф (пункт 1)")
            else:
                compute_distance(g)
        elif choice == "4":
            if g is None:
                print("Сначала загрузите граф (пункт 1).")
            else:
                compute_local_clustering(g)
        elif choice == "5":
            print("Ты клубника я клубника как у нас мог родиться банан")
        elif choice == "0":
            print("Выход")
            break
        else:
            print("Неизвестная команда")

if __name__ == "__main__":
    main()