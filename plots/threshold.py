import matplotlib.pyplot as plt
import numpy as np

from .common import load_csv, short, C, _save


def plot_threshold_sensitivity():
    rows = load_csv("rerankers", "thresholds.csv")
    if not rows:
        return

    models = list(dict.fromkeys(r["model"] for r in rows))
    colors = [C["blue"], C["red"], C["green"], C["amber"], C["purple"]]

    fig, ax = plt.subplots(figsize=(7, 4))
    for ci, model in enumerate(models):
        model_rows = [r for r in rows if r["model"] == model]
        thresholds = [r["threshold"] for r in model_rows]
        f1s = [r["f1"] for r in model_rows]

        c = colors[ci % len(colors)]
        ax.plot(thresholds, f1s, label=short(model), linewidth=1.8, alpha=0.85, color=c)
        best = int(np.argmax(f1s))
        ax.scatter(thresholds[best], f1s[best], s=35, zorder=5, color=c,
                    edgecolors="white", linewidth=0.8)

    ax.axvline(x=0.5, color=C["gray"], linestyle="--", linewidth=0.8, alpha=0.6,
               label="Umbral usado (0.5)")
    ax.set_xlabel("Umbral de decisión")
    ax.set_ylabel("F1")
    ax.set_title("Sensibilidad al umbral de decisión en rerankers")
    ax.legend(fontsize=8, loc="lower left")
    _save(fig, "rerankers", "threshold_sensitivity.png")
