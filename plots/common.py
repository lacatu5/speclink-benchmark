import csv
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

BASE = Path(__file__).parent.parent
OUT = BASE / "results"

sns.set_theme(style="whitegrid", font="sans-serif", font_scale=1.0)

C = {
    "blue": "#3366aa",
    "red": "#c44e52",
    "green": "#4c9f70",
    "amber": "#d4913a",
    "purple": "#7b68a8",
    "gray": "#888888",
    "text": "#444444",
    "text_light": "#777777",
}

MODELS_SHORT = {
    "haiku-4.5": "Claude Haiku 4.5",
    "claude-3-haiku": "Claude 3 Haiku",
    "gpt-4o-mini": "GPT-4o-mini",
    "gpt-oss-120b": "GPT-OSS-120B",
    "gpt-5-nano": "GPT-5-nano",
    "grok-4.1-fast": "Grok-4.1",
    "gemma-4-26b-a4b": "Gemma 4 26B",
    "gemma-4-31b": "Gemma 4 31B",
    "gemini-2.5-flash-lite": "Gemini 2.5 Flash",
    "gemini-3.1-flash-lite-preview": "Gemini 3.1 Flash",
    "mimo-v2.5": "Mimo v2.5",
    "deepseek-v4-flash": "DeepSeek v4",
    "voyage-rerank-2.5": "Voyage 2.5",
    "voyage-rerank-2.5-lite": "Voyage 2.5 Lite",
    "bge-reranker-base": "BGE Base",
    "bge-reranker-v2-m3": "BGE v2-m3",
    "jina": "Jina v3",
}


def short(m):
    return MODELS_SHORT.get(m, m)


def load_csv(folder, filename="data.csv"):
    rows = []
    with open(OUT / folder / filename) as f:
        for r in csv.DictReader(f):
            for k, v in r.items():
                try:
                    r[k] = float(v)
                except (ValueError, TypeError):
                    pass
            rows.append(r)
    return rows


def _save(fig, folder, name):
    d = OUT / folder
    d.mkdir(parents=True, exist_ok=True)
    fig.savefig(d / name, dpi=200, bbox_inches="tight")
    plt.close(fig)
