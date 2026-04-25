import matplotlib.pyplot as plt
import numpy as np

from .common import load_csv, C, _save


def plot_ablation():
    rows = load_csv("ablation")
    pretty = ["Baseline\n(todos los pares)", "Solo\nclasificador", "Solo\nreranker", "Pipeline\ncompleto"]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = np.arange(len(pretty))
    w = 0.2

    ax.bar(x - w, [r["p"] for r in rows], w, label="Precision", color=C["blue"], alpha=0.8)
    ax.bar(x, [r["r"] for r in rows], w, label="Recall", color=C["red"], alpha=0.8)
    ax.bar(x + w, [r["f1"] for r in rows], w, label="F1", color=C["green"], alpha=0.8)

    for i, r in enumerate(rows):
        ax.text(x[i] - w, r["p"] + 0.01, f"{r['p']:.2f}", ha="center", fontsize=8, color=C["text"])
        ax.text(x[i], r["r"] + 0.01, f"{r['r']:.2f}", ha="center", fontsize=8, color=C["text"])
        ax.text(x[i] + w, r["f1"] + 0.01, f"{r['f1']:.2f}", ha="center", fontsize=8, color=C["text"])

    ax.set_xticks(x)
    ax.set_xticklabels(pretty)
    ax.set_ylabel("Puntuación")
    ax.set_title("Estudio de ablación: contribución de componentes")
    ax.legend(fontsize=9)
    ax.set_ylim(-0.1, 1.08)
    _save(fig, "ablation", "ablation.png")
