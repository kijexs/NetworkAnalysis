# построение всех графиков
import os

import matplotlib.pyplot as plt


def plot_degree_distribution(dist, dataset_name, output_dir="results"):
    if not dist:
        return
    os.makedirs(output_dir, exist_ok=True)
    degrees = sorted(dist.keys())
    probs = [dist[k] for k in degrees]

    # обычный график
    plt.figure()
    plt.plot(degrees, probs, "o-", markersize=3)
    plt.xlabel("степень")
    plt.ylabel("доля вершин")
    plt.title(f"Степенное распределение – {dataset_name}")
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, f"{dataset_name}_degree_dist.png"))
    plt.close()

    # log-log
    plt.figure()
    plt.loglog(degrees, probs, "o-", markersize=3)
    plt.xlabel("степень (log)")
    plt.ylabel("доля вершин (log)")
    plt.title(f"Степенное распределение (log-log) – {dataset_name}")
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, f"{dataset_name}_degree_dist_loglog.png"))
    plt.close()
