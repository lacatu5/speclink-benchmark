#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

from evaluation.core import load_ground_truth, BASE
from evaluation.collect import process_path, collect_rows
from evaluation.write_data import write_experiment_data
from evaluation.report import report


def main():
    parser = argparse.ArgumentParser(description="Evalúa experimentos de clasificador/reranker contra ground truth")
    parser.add_argument("targets", nargs="*", help="Files or directories to evaluate")
    parser.add_argument("--no-plots", action="store_true", help="Skip plot generation")
    args = parser.parse_args()

    gt = load_ground_truth()
    print(f"Ground truth: {len(gt)} enlaces positivos")

    if args.targets:
        targets = [Path(t).resolve() for t in args.targets]
    else:
        experiments = BASE / "experiments"
        targets = [experiments / "classifier", experiments / "reranker",
                   experiments / "ablation", experiments / "dspy"]

    for t in targets:
        if t.exists():
            process_path(t, gt)

    rows = []
    for t in targets:
        rows.extend(collect_rows(t, gt))

    if rows:
        write_experiment_data(rows, gt)

    report(rows, gt)

    if not args.no_plots:
        from plots import run_all
        run_all()


if __name__ == "__main__":
    main()
