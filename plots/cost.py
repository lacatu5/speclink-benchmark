import matplotlib.pyplot as plt

from .common import load_csv, short, C, _save


def plot_cost_efficiency():
    rows = load_csv("cost")
    if not rows:
        print("  Skipping cost: cost/data.csv not found")
        return

    names = [short(r["model"]) for r in rows]
    f1s = [r["f1"] for r in rows]
    costs_usd = [r["cost_per_run"] for r in rows]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(costs_usd, f1s, s=80, c=C["blue"], edgecolors="white",
                linewidth=0.6, alpha=0.85, zorder=5)

    from adjustText import adjust_text
    texts = []
    for i in range(len(names)):
        texts.append(ax.text(costs_usd[i], f1s[i], names[i],
                              fontsize=10, color="#1a1a1a"))
    adjust_text(texts, ax=ax,
                force_text=(0.5, 1.0),
                expand=(1.2, 1.4),
                lim=500)

    ax.set_xlabel("Coste por ejecución (USD)")
    ax.set_ylabel("F1")
    ax.set_title("Coste-eficiencia de clasificadores")
    _save(fig, "cost", "cost_efficiency.png")
