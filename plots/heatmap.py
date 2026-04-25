import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from .common import load_csv, short, _save


def plot_per_doc_heatmap():
    rows = load_csv("per_doc")
    if not rows:
        return

    models = list(dict.fromkeys(r["model"] for r in rows))
    docs = list(dict.fromkeys(r["doc"] for r in rows))

    matrix = np.zeros((len(models), len(docs)))
    for r in rows:
        mi = models.index(r["model"])
        di = docs.index(r["doc"])
        matrix[mi][di] = r["f1"]

    fig, ax = plt.subplots(figsize=(9, 4))
    sns.heatmap(matrix, ax=ax, annot=True, fmt=".2f", cmap="RdYlGn",
                vmin=0.5, vmax=1.0,
                xticklabels=docs,
                yticklabels=[short(m) for m in models],
                linewidths=0.5, linecolor="white",
                cbar_kws={"label": "F1", "shrink": 0.8})
    ax.set_title("F1 por modelo y documento")
    ax.tick_params(length=0)
    _save(fig, "per_doc", "per_doc_heatmap.png")
