import csv
import json
from collections import defaultdict

from .core import aggregate, compute_all_true_baseline, load_costs, load_gt_rows, _f4, OUT, BASE


def write_experiment_data(rows, gt):
    OUT.mkdir(parents=True, exist_ok=True)

    sorted_cls = _write_classifiers(rows)
    _write_rerankers(rows, gt)
    _write_ablation(rows, gt)
    _write_dspy(rows)
    _write_cost(rows, sorted_cls)
    _write_per_doc()

    print(f"Datos escritos en subcarpetas de {OUT}/")


def _write_classifiers(rows):
    cls_rows = [r for r in rows if r["mode"] == "classifier"]
    if not cls_rows:
        return []
    d = OUT / "classifiers"
    d.mkdir(parents=True, exist_ok=True)
    cls = aggregate(cls_rows, lambda r: r["model"])
    sorted_cls = sorted(cls.items(), key=lambda x: x[1]["f1"], reverse=True)
    with open(d / "data.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model", "f1", "f1_std", "p", "p_std", "r", "r_std", "fp", "fn"])
        for name, v in sorted_cls:
            w.writerow([name, _f4(v["f1"]), _f4(v["f1_std"]),
                       _f4(v["p"]), _f4(v["p_std"]),
                       _f4(v["r"]), _f4(v["r_std"]),
                       f"{v['fp']:.1f}", f"{v['fn']:.1f}"])
    return sorted_cls


def _write_rerankers(rows, gt):
    rr_rows = [r for r in rows if r["mode"] == "reranker"]
    if not rr_rows:
        return
    d = OUT / "rerankers"
    d.mkdir(parents=True, exist_ok=True)
    rr = aggregate(rr_rows, lambda r: r["model"])
    sorted_rr = sorted(rr.items(), key=lambda x: x[1]["f1"], reverse=True)
    with open(d / "data.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model", "f1", "p", "r", "tp", "fp", "fn"])
        for name, v in sorted_rr:
            w.writerow([name, _f4(v["f1"]), _f4(v["p"]), _f4(v["r"]),
                       v["tp"], f"{v['fp']:.0f}", f"{v['fn']:.0f}"])

    thresholds = [round(i * 0.05, 2) for i in range(2, 20)]
    reranker_dir = BASE / "experiments" / "reranker"
    if not reranker_dir.exists():
        return
    thr_rows = []
    for rdir in sorted(reranker_dir.iterdir()):
        if not rdir.is_dir():
            continue
        run_file = rdir / "run_1.json"
        if not run_file.exists():
            continue
        with open(run_file) as jf:
            entries = json.load(jf)["entries"]
        for t in thresholds:
            predicted = {(e["doc_file"], e["heading"], e["file"])
                         for e in entries if e.get("score", 0) >= t}
            tp = len(gt & predicted)
            fp = len(predicted - gt)
            fn = len(gt - predicted)
            p = tp / (tp + fp) if (tp + fp) > 0 else 0
            rv = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * p * rv / (p + rv) if (p + rv) > 0 else 0
            thr_rows.append([rdir.name, f"{t:.2f}", _f4(f1)])
    with open(d / "thresholds.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model", "threshold", "f1"])
        w.writerows(thr_rows)


def _write_ablation(rows, gt):
    abl_rows = [r for r in rows if r["mode"] == "ablation"]
    if not abl_rows:
        return
    d = OUT / "ablation"
    d.mkdir(parents=True, exist_ok=True)
    bl = compute_all_true_baseline(gt)
    abl = aggregate(abl_rows, lambda r: r["model"])
    with open(d / "data.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["configuration", "f1", "p", "r", "tp", "fp", "fn"])
        w.writerow(["baseline_all_true", _f4(bl["f1"]), _f4(bl["p"]), _f4(bl["r"]),
                    bl["tp"], bl["fp"], bl["fn"]])
        for name in ["classification only", "reranker only", "speclink pipeline"]:
            if name in abl:
                v = abl[name]
                w.writerow([name, _f4(v["f1"]), _f4(v["p"]), _f4(v["r"]),
                           v["tp"], f"{v['fp']:.0f}", f"{v['fn']:.0f}"])


def _write_dspy(rows):
    dspy_rows = [r for r in rows if r["mode"] == "dspy"]
    if not dspy_rows:
        return
    d = OUT / "dspy"
    d.mkdir(parents=True, exist_ok=True)
    dspy = aggregate(dspy_rows, lambda r: (r["model"], r.get("prompt_type", "")))
    models_dspy = defaultdict(dict)
    for (model, ptype), v in dspy.items():
        models_dspy[model][ptype] = v
    with open(d / "data.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model", "prompt_type", "f1", "p", "r", "fp", "fn", "delta_f1_pp", "delta_fp"])
        for model in sorted(models_dspy):
            t = models_dspy[model]
            for ptype in ["baseline", "optimized"]:
                if ptype in t:
                    v = t[ptype]
                    df1 = ""
                    dfp = ""
                    if ptype == "optimized" and "baseline" in t:
                        delta = t["optimized"]["f1"] - t["baseline"]["f1"]
                        df1 = f"{delta*100:+.1f}"
                        dfp = f"{t['baseline']['fp'] - t['optimized']['fp']:+.1f}"
                    w.writerow([model, ptype, _f4(v["f1"]), _f4(v["p"]), _f4(v["r"]),
                               f"{v['fp']:.1f}", f"{v['fn']:.1f}", df1, dfp])


def _write_cost(rows, sorted_cls):
    costs = load_costs()
    if not costs or not sorted_cls:
        return
    d = OUT / "cost"
    d.mkdir(parents=True, exist_ok=True)
    with open(d / "data.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model", "f1", "p", "r", "fp", "fn", "in_tok", "out_tok",
                    "cost_per_run", "input_per_m", "output_per_m"])
        for name, v in sorted_cls:
            if name in costs:
                c = costs[name]
                total = (v["in_tok"] * c["input"] + v["out_tok"] * c["output"]) / 1_000_000
                w.writerow([name, _f4(v["f1"]), _f4(v["p"]), _f4(v["r"]),
                           f"{v['fp']:.1f}", f"{v['fn']:.1f}",
                           f"{v['in_tok']:.0f}", f"{v['out_tok']:.0f}",
                           _f4(total), c["input"], c["output"]])


def _write_per_doc():
    gt_rows = load_gt_rows()
    experiments_dir = BASE / "experiments" / "classifier"
    if not experiments_dir.exists():
        return
    d = OUT / "per_doc"
    d.mkdir(parents=True, exist_ok=True)
    models_dirs = sorted(p.name for p in experiments_dir.iterdir() if p.is_dir())
    docs = sorted(set(r["doc_file"] for r in gt_rows))
    doc_short = [dp.split("/")[1].replace(".md", "") for dp in docs]
    perdoc_rows = []
    for model in models_dirs:
        run_path = experiments_dir / model / "run_1.json"
        if not run_path.exists():
            continue
        with open(run_path) as jf:
            entries = json.load(jf)["entries"]
        for di, doc in enumerate(docs):
            doc_entries = [e for e in entries if e["doc_file"] == doc]
            doc_gt = {(r["heading"], r["file"]) for r in gt_rows if r["doc_file"] == doc}
            predicted = {(e["heading"], e["file"]) for e in doc_entries if e.get("match")}
            tp = len(doc_gt & predicted)
            fp = len(predicted - doc_gt)
            fn = len(doc_gt - predicted)
            total = tp + fp + fn
            f1 = (2 * tp / (2 * tp + fp + fn)) if total > 0 else 0
            perdoc_rows.append([model, doc_short[di], _f4(f1)])
    with open(d / "data.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model", "doc", "f1"])
        w.writerows(perdoc_rows)
