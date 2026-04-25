from .classifiers import plot_f1_bars, plot_error_breakdown
from .ablation import plot_ablation
from .heatmap import plot_per_doc_heatmap
from .threshold import plot_threshold_sensitivity
from .cost import plot_cost_efficiency

PLOTS = [
    ("F1 clasificadores", plot_f1_bars),
    ("Error breakdown", plot_error_breakdown),
    ("Ablation", plot_ablation),
    ("Heatmap por documento", plot_per_doc_heatmap),
    ("Sensibilidad umbral", plot_threshold_sensitivity),
    ("Coste-eficiencia", plot_cost_efficiency),
]


def run_all():
    for name, fn in PLOTS:
        try:
            fn()
            print(f"  OK  {name}")
        except Exception as e:
            print(f"  ERR {name}: {e}")
    print(f"\nSalida: results/")
