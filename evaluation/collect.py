import statistics
from pathlib import Path

from .core import detect_mode, evaluate, extract_metadata, extract_run_index


def print_row(label, m):
    print(f"  {label:<30} P={m['p']:.3f}  R={m['r']:.3f}  F1={m['f1']:.3f}  TP={m['tp']}  FP={m['fp']}  FN={m['fn']}")


def process_path(target, gt):
    target = Path(target)
    if not target.exists():
        print(f"No encontrado: {target}")
        return

    if target.is_file():
        mode, data = detect_mode(target)
        if not mode:
            print(f"Formato desconocido: {target}")
            return
        m = evaluate(data["entries"], gt, mode)
        model = data.get("model", target.stem)
        print(f"\n[{mode}] {model}")
        print_row(target.name, m)
        if "input_tokens" in data:
            print(f"  tokens: {data['input_tokens']} in / {data['output_tokens']} out")

    elif target.is_dir():
        json_files = sorted(target.rglob("*.json"))
        if not json_files:
            print(f"Sin archivos JSON en {target}")
            return

        grouped = {}
        for jf in json_files:
            mode, data = detect_mode(jf)
            if not mode:
                continue
            model = data.get("model", jf.parent.name)
            grouped.setdefault(mode, {}).setdefault(model, []).append(
                (jf, data, evaluate(data["entries"], gt, mode))
            )

        for mode, models in grouped.items():
            print(f"\n{'='*80}")
            print(f"  {mode.upper()} — {target}")
            print(f"{'='*80}")
            print(f"  {'Model':<30} {'P':<8} {'R':<8} {'F1':<8} {'TP':<5} {'FP':<5} {'FN':<5}")
            print(f"  {'-'*72}")

            for model, runs in models.items():
                for i, (_, data, m) in enumerate(runs):
                    print(f"  {model:<30} {m['p']:<8.3f} {m['r']:<8.3f} {m['f1']:<8.3f} {m['tp']:<5} {m['fp']:<5} {m['fn']:<5}")
                ps = [r[2]["p"] for r in runs]
                rs = [r[2]["r"] for r in runs]
                f1s = [r[2]["f1"] for r in runs]
                print(f"  {'  mean':<30} {statistics.mean(ps):<8.3f} {statistics.mean(rs):<8.3f} {statistics.mean(f1s):<8.3f}")
                if len(runs) > 1:
                    print(f"  {'  std':<30} {statistics.stdev(ps):<8.3f} {statistics.stdev(rs):<8.3f} {statistics.stdev(f1s):<8.3f}")
                print()


def collect_rows(target, gt):
    target = Path(target)
    if not target.exists():
        return []

    if target.is_file():
        mode, data = detect_mode(target)
        if not mode:
            return []
        m = evaluate(data["entries"], gt, mode)
        detected_mode, model, prompt_type = extract_metadata(target)
        return [{
            "mode": detected_mode or mode,
            "model": model or data.get("model", target.stem),
            "prompt_type": prompt_type or "",
            "run": extract_run_index(target),
            "P": round(m["p"], 4),
            "R": round(m["r"], 4),
            "F1": round(m["f1"], 4),
            "TP": m["tp"],
            "FP": m["fp"],
            "FN": m["fn"],
            "input_tokens": int(data.get("input_tokens", 0) or 0),
            "output_tokens": int(data.get("output_tokens", 0) or 0),
        }]

    rows = []
    for jf in sorted(target.rglob("*.json")):
        mode, data = detect_mode(jf)
        if not mode:
            continue
        m = evaluate(data["entries"], gt, mode)
        detected_mode, model, prompt_type = extract_metadata(jf)
        rows.append({
            "mode": detected_mode or mode,
            "model": model or data.get("model", jf.parent.name),
            "prompt_type": prompt_type or "",
            "run": extract_run_index(jf),
            "P": round(m["p"], 4),
            "R": round(m["r"], 4),
            "F1": round(m["f1"], 4),
            "TP": m["tp"],
            "FP": m["fp"],
            "FN": m["fn"],
            "input_tokens": int(data.get("input_tokens", 0) or 0),
            "output_tokens": int(data.get("output_tokens", 0) or 0),
        })
    return rows
