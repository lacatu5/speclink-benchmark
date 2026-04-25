import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from .common import load_csv, short, C, _save


def plot_f1_bars():
    rows = load_csv("classifiers")
    names = [short(r["model"]) for r in rows]
    f1s = [r["f1"] for r in rows]
    stds = [r.get("f1_std", 0) for r in rows]

    fig, ax = plt.subplots(figsize=(7, 4))
    palette = sns.color_palette("Blues_d", len(names))
    bars = ax.barh(names, f1s, xerr=stds, color=palette, capsize=3, height=0.55,
                    edgecolor="white", linewidth=0.3,
                    error_kw={"lw": 0.8, "capthick": 0.8})

    for bar, val, std in zip(bars, f1s, stds):
        label = f"{val:.3f}" if std == 0 else f"{val:.3f} \u00b1{std:.3f}"
        ax.text(bar.get_width() + 0.012, bar.get_y() + bar.get_height() / 2,
                label, va="center", fontsize=8, color=C["text"])

    ax.set_xlim(0.7, 0.93)
    ax.set_xlabel("F1")
    ax.set_title("Rendimiento de clasificadores LLM (media \u00b1 desv. est., n=3)")
    ax.invert_yaxis()
    _save(fig, "classifiers", "f1_classifiers.png")


def plot_error_breakdown():
    rows = load_csv("classifiers")
    sorted_rows = sorted(rows, key=lambda r: r["fp"] + r["fn"])
    names = [short(r["model"]) for r in sorted_rows]
    fps = [r["fp"] for r in sorted_rows]
    fns = [r["fn"] for r in sorted_rows]

    fig, ax = plt.subplots(figsize=(7, 4))
    y = np.arange(len(names))

    ax.barh(y, fps, height=0.5, label="Falsos positivos", color=C["red"], alpha=0.7)
    ax.barh(y, fns, height=0.5, left=fps, label="Falsos negativos", color=C["blue"], alpha=0.7)

    for i, (fp, fn) in enumerate(zip(fps, fns)):
        if fp > 0:
            ax.text(fp / 2, i, f"{fp:.0f}", ha="center", va="center", fontsize=8, color="white")
        ax.text(fp + fn / 2, i, f"{fn:.0f}", ha="center", va="center", fontsize=8, color="white")
        ax.text(fp + fn + 0.8, i, f"{fp + fn:.0f}", va="center", fontsize=8, color=C["text_light"])

    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=8)
    ax.set_xlabel("Errores")
    ax.set_title("Desglose de errores: FP vs FN por clasificador")
    ax.legend(fontsize=9, loc="lower right")
    _save(fig, "classifiers", "error_breakdown.png")
