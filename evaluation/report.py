from collections import defaultdict

from .core import aggregate, compute_all_true_baseline, load_costs, load_gt_rows, _f4, OUT


def report(rows, gt):
    gt_rows = load_gt_rows()
    costs = load_costs()

    print("=" * 80)
    print("REPORTE — Datos para iteracion3.tex")
    print("=" * 80)

    doc_files = sorted(set(r["doc_file"] for r in gt_rows))
    src_files = sorted(set(r["file"] for r in gt_rows))
    headings = len(set((r["doc_file"], r["heading"]) for r in gt_rows))
    print(f"\n[GROUND TRUTH]")
    print(f"  Enlaces únicos: {len(gt)}")
    print(f"  Archivos fuente: {len(src_files)}")
    print(f"  Archivos doc: {len(doc_files)}")
    print(f"  Secciones: {headings}")

    bl = compute_all_true_baseline(gt)
    print(f"\n[BASELINE — todos TRUE ({bl['pairs']} pares)]")
    print(f"  P={_f4(bl['p'])}  R={_f4(bl['r'])}  F1={_f4(bl['f1'])}  TP={bl['tp']}  FP={bl['fp']}  FN={bl['fn']}")

    if not rows:
        print("\nSin datos de experimentos.")
        return

    abl = aggregate([r for r in rows if r["mode"] == "ablation"], lambda r: r["model"])
    if abl:
        print(f"\n[ABLACIÓN]")
        print(f"  {'Configuración':<30} {'F1':<8} {'P':<8} {'R':<8} {'FP':<6} {'FN':<6}")
        for name in ["classification only", "reranker only", "speclink pipeline"]:
            if name in abl:
                v = abl[name]
                print(f"  {name:<30} {_f4(v['f1']):<8} {_f4(v['p']):<8} {_f4(v['r']):<8} {v['fp']:<6.0f} {v['fn']:<6.0f}")

    cls_rows_list = [r for r in rows if r["mode"] == "classifier"]
    sorted_cls = []
    if cls_rows_list:
        cls = aggregate(cls_rows_list, lambda r: r["model"])
        sorted_cls = sorted(cls.items(), key=lambda x: x[1]["f1"], reverse=True)
        print(f"\n[CLASIFICADORES — promedio {sorted_cls[0][1]['n']} runs]")
        print(f"  {'Modelo':<30} {'F1':<8} {'P':<8} {'R':<8} {'FP':<8} {'FN':<8}")
        for name, v in sorted_cls:
            print(f"  {name:<30} {_f4(v['f1']):<8} {_f4(v['p']):<8} {_f4(v['r']):<8} {v['fp']:<8.1f} {v['fn']:<8.1f}")

    rr_rows_list = [r for r in rows if r["mode"] == "reranker"]
    if rr_rows_list:
        rr = aggregate(rr_rows_list, lambda r: r["model"])
        sorted_rr = sorted(rr.items(), key=lambda x: x[1]["f1"], reverse=True)
        print(f"\n[RERANKERS — umbral ≥ 0.5]")
        print(f"  {'Modelo':<30} {'F1':<8} {'P':<8} {'R':<8} {'FP':<6} {'FN':<6}")
        for name, v in sorted_rr:
            print(f"  {name:<30} {_f4(v['f1']):<8} {_f4(v['p']):<8} {_f4(v['r']):<8} {v['fp']:<6.0f} {v['fn']:<6.0f}")

    dspy_rows_list = [r for r in rows if r["mode"] == "dspy"]
    if dspy_rows_list:
        dspy = aggregate(dspy_rows_list, lambda r: (r["model"], r.get("prompt_type", "")))
        print(f"\n[DSPy — baseline vs optimized]")
        print(f"  {'Modelo':<20} {'Tipo':<12} {'F1':<8} {'P':<8} {'R':<8} {'FP':<6} {'FN':<6}")
        models_dspy = defaultdict(dict)
        for (model, ptype), v in dspy.items():
            models_dspy[model][ptype] = v
            print(f"  {model:<20} {ptype:<12} {_f4(v['f1']):<8} {_f4(v['p']):<8} {_f4(v['r']):<8} {v['fp']:<6.1f} {v['fn']:<6.1f}")
        print(f"\n  Deltas:")
        for model in sorted(models_dspy):
            t = models_dspy[model]
            if "baseline" in t and "optimized" in t:
                df1 = t["optimized"]["f1"] - t["baseline"]["f1"]
                dfp = t["baseline"]["fp"] - t["optimized"]["fp"]
                print(f"    {model:<20} ΔF1={df1:+.4f} ({df1*100:+.1f}pp)  ΔFP={dfp:+.1f}")

    if costs and sorted_cls:
        print(f"\n[COSTE-EFICIENCIA]")
        print(f"  {'Modelo':<30} {'in_tok':<10} {'out_tok':<10} {'cost/run':<10} {'F1':<8}")
        cost_entries = []
        for name, v in sorted_cls:
            if name in costs:
                c = costs[name]
                total = (v["in_tok"] * c["input"] + v["out_tok"] * c["output"]) / 1_000_000
                if total > 0:
                    print(f"  {name:<30} {v['in_tok']:<10.0f} {v['out_tok']:<10.0f} ${total:<9.4f} {_f4(v['f1']):<8}")
                    cost_entries.append((total, name, v["f1"]))
        if cost_entries:
            min_c = min(e[0] for e in cost_entries)
            max_c = max(e[0] for e in cost_entries)
            print(f"\n  Rango coste/ejecución: ${min_c:.4f} — ${max_c:.4f}")

    pngs = sorted(f.name for f in OUT.rglob("*.png")) if OUT.exists() else []
    print(f"\n[VISUALIZACIONES] ({len(pngs)} gráficos)")
    for p in pngs:
        print(f"  {p}")

    print(f"\n{'='*80}")
    print("[RESUMEN CLAVE para iteracion3.tex]")
    print(f"{'='*80}")
    print(f"  GT: {len(gt)} enlaces, {len(src_files)} archivos fuente, {len(doc_files)} docs, {headings} secciones")
    print(f"  Baseline all-TRUE: F1={_f4(bl['f1'])} FP={bl['fp']}")
    if sorted_cls:
        best = sorted_cls[0]
        print(f"  Mejor modelo: {best[0]} F1={_f4(best[1]['f1'])} (±{_f4(best[1]['f1_std'])})")
        top3 = ", ".join(_f4(v["f1"]) for _, v in sorted_cls[:3])
        print(f"  Top-3 F1: {top3}")
    if costs and sorted_cls and cost_entries:
        print(f"  Coste range: ${min_c:.3f} — ${max_c:.3f}")
    print(f"  Visualizaciones: {len(pngs)}")
    if abl and "classification only" in abl and "speclink pipeline" in abl:
        fp_start = abl["classification only"]["fp"]
        fp_end = abl["speclink pipeline"]["fp"]
        print(f"  Ablación FP: clasif-only={fp_start:.0f} → pipeline={fp_end:.0f} (reducción {(1-fp_end/fp_start)*100:.0f}%)")
