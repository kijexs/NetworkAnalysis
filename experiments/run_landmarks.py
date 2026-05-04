# запуск и сравнение алгоритмов
import csv
import os
import random
import time
from typing import List

from experiments.plot_results import plot_landmarks_results
from src.analysis import largest_cc_vertices
from src.graph import Graph
from src.landmarks import (
    LandmarksBasic,
    LandmarksSC,
    select_best_coverage_landmarks,
    select_degree_landmarks,
    select_random_landmarks,
)
from src.utils import bfs

DATASET_ROOT = "datasets"
OUTPUT_DIR = "results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# параметры экспериментов
KS = [5, 10, 20, 50]  # количество ориентиров
STRATEGIES = ["random", "degree", "coverage"]
NUM_PAIRS = 100  # сколько случайных пар вершин тестируем
COVERAGE_M = 200  # параметр M для Best-Coverage


def load_graph(filepath: str) -> Graph:
    norm = os.path.normpath(filepath)
    directed = "directed" in norm.split(os.sep)
    return Graph.from_file(filepath, directed=directed)


def collect_all_files(root: str) -> List[str]:
    all_files = []
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            all_files.append(os.path.join(dirpath, fname))
    return all_files


def run():
    global landmarks
    all_files = collect_all_files(DATASET_ROOT)
    results_csv = os.path.join(OUTPUT_DIR, "landmarks_results.csv")
    with open(results_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "graph",
                "k",
                "strategy",
                "basic_prep_time",
                "sc_prep_time",
                "basic_query_time",
                "sc_query_time",
                "basic_mre",
                "sc_mre",
                "basic_exact_frac",
                "sc_exact_frac",
            ]
        )

    for filepath in all_files:
        name = os.path.relpath(filepath, DATASET_ROOT).replace("/", "_").replace(".", "_")
        print(f"\n===== {name} =====")
        g = load_graph(filepath)

        # работаем с наибольшей компонентой связности
        lcc_verts = largest_cc_vertices(g)
        print(f"  Наибольшая компонента: {len(lcc_verts)} вершин")

        # генерируем тестовые пары
        nodes_lcc = list(lcc_verts)
        if len(nodes_lcc) < 2:
            print("  Недостаточно вершин для пар")
            continue

        random.seed(40)  # для воспроизводимости
        pairs = []
        while len(pairs) < NUM_PAIRS:
            a = random.choice(nodes_lcc)
            b = random.choice(nodes_lcc)
            if a != b:
                pairs.append((a, b))

        # вычисляем эталонные расстояния
        print("  Вычисление эталонных расстояний...")
        exact_dist = []
        t0 = time.time()
        for u, v in pairs:
            dist_u = bfs(g, u)
            if v in dist_u:
                exact_dist.append(dist_u[v])
            else:
                exact_dist.append(-1)  # не должно случиться, т.к. в одной компоненте
        exact_time = time.time() - t0
        print(f"  Эталонные расстояния: {exact_time:.2f} с")

        # словарь для сбора результатов по каждому k и стратегии,
        # чтобы затем построить графики
        basic_prep_times = {}  # (k, strategy) -> time
        sc_prep_times = {}
        basic_query_times = {}
        sc_query_times = {}
        basic_mre = {}
        sc_mre = {}
        basic_exact_frac = {}
        sc_exact_frac = {}

        for k in KS:
            for strat in STRATEGIES:
                print(f"  k={k}, стратегия {strat}")
                # выбираем ориентиры
                if strat == "random":
                    landmarks = select_random_landmarks(g, k)
                elif strat == "degree":
                    landmarks = select_degree_landmarks(g, k)
                elif strat == "coverage":
                    landmarks = select_best_coverage_landmarks(g, k, M=COVERAGE_M)

                # LandmarksBasic
                t0 = time.time()
                lb = LandmarksBasic(g, landmarks)
                prep_basic = time.time() - t0

                t0 = time.time()
                est_basic = [lb.estimate(u, v) for u, v in pairs]
                query_basic = time.time() - t0

                # LandmarksSC
                t0 = time.time()
                lsc = LandmarksSC(g, landmarks)
                prep_sc = time.time() - t0

                t0 = time.time()
                est_sc = [lsc.estimate(u, v) for u, v in pairs]
                query_sc = time.time() - t0

                # точность
                mre_basic_list = []
                mre_sc_list = []
                exact_basic = 0
                exact_sc = 0
                valid = 0
                for true_d, e_b, e_s in zip(exact_dist, est_basic, est_sc):
                    if true_d == -1:
                        continue
                    valid += 1
                    if true_d == 0:
                        if e_b == 0:
                            exact_basic += 1
                            mre_basic_list.append(0.0)
                        else:
                            mre_basic_list.append(1.0)  # большая ошибка
                        if e_s == 0:
                            exact_sc += 1
                            mre_sc_list.append(0.0)
                        else:
                            mre_sc_list.append(1.0)
                    else:
                        if e_b == true_d:
                            exact_basic += 1
                        if e_s == true_d:
                            exact_sc += 1
                        rel_err_basic = abs(e_b - true_d) / true_d if e_b != -1 else 1.0
                        rel_err_sc = abs(e_s - true_d) / true_d if e_s != -1 else 1.0
                        mre_basic_list.append(rel_err_basic)
                        mre_sc_list.append(rel_err_sc)

                if valid > 0:
                    avg_mre_basic = sum(mre_basic_list) / valid
                    avg_mre_sc = sum(mre_sc_list) / valid
                    frac_basic = exact_basic / valid
                    frac_sc = exact_sc / valid
                else:
                    avg_mre_basic = avg_mre_sc = 0.0
                    frac_basic = frac_sc = 0.0

                # сохраняем метрики для графиков
                key = (k, strat)
                basic_prep_times[key] = prep_basic
                sc_prep_times[key] = prep_sc
                basic_query_times[key] = query_basic
                sc_query_times[key] = query_sc
                basic_mre[key] = avg_mre_basic
                sc_mre[key] = avg_mre_sc
                basic_exact_frac[key] = frac_basic
                sc_exact_frac[key] = frac_sc

                # запись в csv
                with open(results_csv, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(
                        [
                            name,
                            k,
                            strat,
                            prep_basic,
                            prep_sc,
                            query_basic,
                            query_sc,
                            avg_mre_basic,
                            avg_mre_sc,
                            frac_basic,
                            frac_sc,
                        ]
                    )

        # строим графики для данного графа
        try:
            plot_landmarks_results(
                name,
                KS,
                STRATEGIES,
                basic_mre,
                sc_mre,
                basic_exact_frac,
                sc_exact_frac,
                basic_query_times,
                sc_query_times,
                basic_prep_times,
                sc_prep_times,
                output_dir=OUTPUT_DIR,
            )
        except Exception as e:
            print(f"  Ошибка при построении графиков: {e}")

    print("\nЭксперименты завершены. Результаты в", OUTPUT_DIR)


if __name__ == "__main__":
    run()
