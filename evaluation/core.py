import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).parent.parent
GT_PATH = BASE / "data" / "ground-truth.csv"
BL_PATH = BASE / "data" / "baseline.csv"
COSTS_PATH = BASE / "data" / "model_costs.csv"
OUT = BASE / "results"


def load_ground_truth():
    gt = set()
    with open(GT_PATH) as f:
        for row in csv.DictReader(f):
            gt.add((row["doc_file"], row["heading"], row["file"]))
    return gt


def load_gt_rows():
    with open(GT_PATH) as f:
        return list(csv.DictReader(f))


def load_costs():
    costs = {}
    if not COSTS_PATH.exists():
        return costs
    with open(COSTS_PATH) as f:
        for row in csv.DictReader(f):
            costs[row["model"]] = {
                "input": float(row["input_per_m"]),
                "output": float(row["output_per_m"]),
            }
    return costs


def evaluate(entries, gt, mode, threshold=0.5):
    predicted = set()
    for e in entries:
        if mode == "classifier":
            if e.get("match"):
                predicted.add((e["doc_file"], e["heading"], e["file"]))
        elif mode == "reranker":
            if e.get("score", 0) >= threshold:
                predicted.add((e["doc_file"], e["heading"], e["file"]))
    tp = len(gt & predicted)
    fp = len(predicted - gt)
    fn = len(gt - predicted)
    p = tp / (tp + fp) if (tp + fp) > 0 else 0
    r = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0
    return {"p": p, "r": r, "f1": f1, "tp": tp, "fp": fp, "fn": fn}


def detect_mode(path):
    with open(path) as f:
        data = json.load(f)
    if "entries" not in data:
        return None, None
    first = data["entries"][0]
    if "match" in first:
        return "classifier", data
    if "score" in first:
        return "reranker", data
    return None, None


def extract_run_index(path):
    stem = Path(path).stem
    if stem.startswith("run_"):
        try:
            return int(stem.split("_")[1])
        except (IndexError, ValueError):
            pass
    return 1


def extract_metadata(path):
    path = Path(path)
    parts = path.relative_to(BASE / "experiments").parts
    mode = parts[0]
    model = prompt_type = None
    if mode == "classifier":
        model = parts[1]
    elif mode == "reranker":
        model = parts[1]
    elif mode == "ablation":
        model = path.stem.replace("_", " ")
    elif mode == "dspy":
        model = parts[1]
        if len(parts) >= 3 and parts[2] in ("baseline", "optimized"):
            prompt_type = parts[2]
    return mode, model, prompt_type


def aggregate(rows, key_fn):
    groups = defaultdict(list)
    for r in rows:
        groups[key_fn(r)].append(r)
    result = {}
    for k, runs in groups.items():
        n = len(runs)
        result[k] = {
            "p": statistics.mean(r["P"] for r in runs),
            "r": statistics.mean(r["R"] for r in runs),
            "f1": statistics.mean(r["F1"] for r in runs),
            "p_std": statistics.stdev(r["P"] for r in runs) if n > 1 else 0,
            "r_std": statistics.stdev(r["R"] for r in runs) if n > 1 else 0,
            "f1_std": statistics.stdev(r["F1"] for r in runs) if n > 1 else 0,
            "tp": runs[0]["TP"],
            "fp": statistics.mean(r["FP"] for r in runs),
            "fn": statistics.mean(r["FN"] for r in runs),
            "n": n,
            "in_tok": statistics.mean(r["input_tokens"] for r in runs) if runs[0]["input_tokens"] else 0,
            "out_tok": statistics.mean(r["output_tokens"] for r in runs) if runs[0]["output_tokens"] else 0,
        }
    return result


def compute_all_true_baseline(gt):
    pairs = set()
    with open(BL_PATH) as f:
        for row in csv.DictReader(f):
            pairs.add((row["doc_file"], row["heading"], row["file"]))
    tp = len(gt & pairs)
    fp = len(pairs - gt)
    fn = len(gt - pairs)
    p = tp / (tp + fp) if (tp + fp) else 0
    r = tp / (tp + fn) if (tp + fn) else 0
    f1 = 2 * p * r / (p + r) if (p + r) else 0
    return {"p": p, "r": r, "f1": f1, "tp": tp, "fp": fp, "fn": fn, "pairs": len(pairs)}


def _f4(v):
    return f"{v:.4f}"
