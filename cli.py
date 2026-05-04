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
from src.landmarks import LandmarksBasic, LandmarksSC, select_random_landmarks, select_degree_landmarks, \
    select_best_coverage_landmarks
from src.analysis import degree_distribution
from experiments.plot_results import plot_degree_distribution
from src.robustness import evaluate_robustness, random_removal, degree_based_removal
from experiments.plot_results import plot_robustness
from src.utils import bfs

# глобальные переменные для результатов последней симуляции устойчивости
_rand_res = None
_deg_res = None

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

def run_robustness_simulation(g):
    global _rand_res, _deg_res
    print("\nИсследование устойчивости сети")
    percentages = list(range(0, 101, 10))
    print("1. Случайное удаление...")
    _rand_res = evaluate_robustness(g, percentages, random_removal)
    print("2. Удаление по наибольшей степени...")
    _deg_res = evaluate_robustness(g, percentages, degree_based_removal)

    print("\n% удалённых | доля в МК (random) | доля в МК (degree)")
    for (p, r), (_, d) in zip(_rand_res, _deg_res):
        print(f"{p:3d}%        | {r:.4f}              | {d:.4f}")

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
        print("6. Графики (распределение степеней и устойчивость)")
        print("7. Сравнение Landmarks (Basic vs SC)")
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
                print("Сначала загрузите граф (пункт 1)")
            else:
                compute_local_clustering(g)
        elif choice == "5":
            if g is None:
                print("Сначала загрузите граф (пункт 1)")
            else:
                run_robustness_simulation(g)
        elif choice == "6":
            if g is None:
                print("Сначала загрузите граф (пункт 1)")
            else:
                # график степеней
                dist = degree_distribution(g)
                plot_degree_distribution(dist, "current_graph")
                print("График распределения степеней сохранён в results/")

                # график устойчивости, если симуляция была проведена
                if _rand_res is not None and _deg_res is not None:
                    plot_robustness(_rand_res, _deg_res, name="interactive")
                    print("График устойчивости сохранён в results/robustness_interactive.png")
                else:
                    print("Симуляция устойчивости ещё не проводилась. Выполните пункт 5")
        elif choice == "7":
            if g is None:
                print("Сначала загрузите граф (пункт 1)")
                continue

            try:
                u = int(input("Введите вершину u: "))
                v = int(input("Введите вершину v: "))
            except ValueError:
                print("Некорректный ввод")
                continue

            # эталонное расстояние  bfs
            dist_map = bfs(g, u)
            exact = dist_map.get(v)
            if exact is None:
                print(f"Между {u} и {v} нет пути")
                continue
            print(f"Эталонное расстояние: {exact}")

            # выбор стратегии
            print("\nСтратегии выбора ориентиров:")
            print("  1 – случайные вершины")
            print("  2 – вершины с наибольшей степенью")
            print("  3 – наилучшее покрытие (best coverage)")
            strat_choice = input("Выберите стратегию (1/2/3): ").strip()

            try:
                k = int(input("Количество ориентиров (например, 10): "))
            except ValueError:
                print("Некорректное число, используется 10")
                k = 20

            # выбор ориентиров согласно стратегии
            if strat_choice == "1":
                landmarks = select_random_landmarks(g, k)
            elif strat_choice == "2":
                landmarks = select_degree_landmarks(g, k)
            elif strat_choice == "3":
                try:
                    M = int(input("Размер выборки для coverage (по умолчанию 500): ") or 500)
                except ValueError:
                    M = 500
                print(f"Вычисление best-coverage ориентиров (M={M})...")
                landmarks = select_best_coverage_landmarks(g, k, M=M)
            else:
                print("Неизвестная стратегия, используются случайные")
                landmarks = select_random_landmarks(g, k)

            # создаём оценки
            lb = LandmarksBasic(g, landmarks)
            lsc = LandmarksSC(g, landmarks)

            print("\nРезультаты оценки расстояний:")
            print(f"  Landmarks-Basic: {lb.estimate(u, v)}")
            print(f"  Landmarks-SC   : {lsc.estimate(u, v)}")
        elif choice == "0":
            print("Выход")
            break
        else:
            print("Неизвестная команда")

if __name__ == "__main__":
    main()