#!/usr/bin/env python3
"""DSPy MIPROv2 zero-shot prompt optimizer for speclink's traceability classifier.

The dataset (classifier-dataset.csv) contains pairs that survived the reranker's
0.5 score threshold — i.e. candidate section-file pairs already deemed plausible
by the retrieval pipeline. This models real usage: the classifier only sees pairs
the reranker didn't discard.
"""
import csv
import os
import random
import sys
from pathlib import Path
from typing import Literal

import yaml
from dotenv import load_dotenv
import dspy

logging = __import__("logging")
logging.getLogger("dspy").setLevel(logging.WARNING)

HERE = Path(__file__).resolve().parent
DATASET_PATH = HERE.parent / "data" / "dspy-dataset.csv"
CODE_ROOT = HERE.parent / "code"
SPECLINK_ROOT = HERE.parent.parent / "speclink"
BASELINE_PROMPT = HERE.parent / "experiments" / "dspy" / "classification_baseline.yaml"


def load_baseline_system():
    return yaml.safe_load(BASELINE_PROMPT.read_text()).get("system", "")


class TraceabilityClassification(dspy.Signature):
    __doc__ = load_baseline_system()
    source: str = dspy.InputField(desc="Documentation section with heading and content")
    target: str = dspy.InputField(desc="Source file path and code content")
    decision: Literal["TRUE", "FALSE"] = dspy.OutputField(
        desc="TRUE if changing this file would require updating this documentation"
    )


class TraceabilityClassifier(dspy.Module):
    def __init__(self):
        self.classify = dspy.ChainOfThought(TraceabilityClassification)

    def forward(self, source: str, target: str):
        return self.classify(source=source, target=target)


def f1_metric(gold, pred, trace=None) -> float:
    return 1.0 if pred.decision.strip().upper() == gold.label else 0.0


def compute_f1(classifier, examples):
    tp = fp = fn = 0
    for ex in examples:
        pred = classifier(**ex.inputs()).decision.strip().upper()
        if pred == "TRUE" and ex.label == "TRUE":
            tp += 1
        elif pred == "TRUE" and ex.label == "FALSE":
            fp += 1
        elif pred == "FALSE" and ex.label == "TRUE":
            fn += 1
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    return 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0


def extract_instruction(optimized):
    mod = optimized.classify
    inner = getattr(mod, "predict", mod)
    sig = getattr(inner, "signature", None)
    instruction = getattr(sig, "instructions", None) if sig else None
    if isinstance(instruction, str) and "StringSignature" not in instruction:
        return instruction
    return str(sig or mod)


def main():
    load_dotenv()
    dspy.configure(lm=dspy.LM(os.environ["LLM_MODEL"], api_key=os.environ["LLM_API_KEY"]))

    raw_pairs = []
    with open(DATASET_PATH, newline="") as f:
        for row in csv.DictReader(f):
            raw_pairs.append((row["doc_file"], row["heading"], row["file"], row["label"]))

    sys.path.insert(0, str(SPECLINK_ROOT))
    from speclink.preprocessing.code_extraction import EXTRACTORS

    lang_map = {".py": "python", ".js": "javascript", ".jsx": "javascript", ".ts": "typescript", ".tsx": "typescript"}
    file_signatures = {}
    for path in CODE_ROOT.rglob("*"):
        if path.suffix in lang_map and "__pycache__" not in path.parts and "node_modules" not in path.parts:
            try:
                result = EXTRACTORS[lang_map[path.suffix]](path.read_bytes(), path, CODE_ROOT)
                parts = [f"File: {path.relative_to(CODE_ROOT)}"]
                sigs = [s["signature"] for s in result["symbols"]]
                if sigs:
                    parts.append("Signatures:\n" + "\n".join(f"  {s}" for s in sigs))
                if result["variables"]:
                    parts.append("Variables:\n" + "\n".join(f"  {v}" for v in result["variables"]))
                file_signatures[str(path.relative_to(CODE_ROOT))] = "\n".join(parts)
            except Exception:
                pass

    doc_sections = {}
    for doc_path in sorted(CODE_ROOT.glob("docs/*.md")):
        doc_rel = str(doc_path.relative_to(CODE_ROOT))
        heading, lines, sections = "", [], {}
        for line in doc_path.read_text().splitlines():
            if line.startswith("#"):
                if heading:
                    sections[heading] = "\n".join(lines).strip()
                heading, lines = line.lstrip("#").strip(), []
            else:
                lines.append(line)
        if heading:
            sections[heading] = "\n".join(lines).strip()
        doc_sections[doc_rel] = sections

    pairs = []
    for doc, heading, fp, label in raw_pairs:
        if fp not in file_signatures:
            continue
        section_text = doc_sections.get(doc, {}).get(heading, "")
        source_content = f"{heading}\n\n{section_text}" if section_text else heading
        pairs.append({"source": source_content, "target": file_signatures[fp], "label": label})

    random.shuffle(pairs)
    split = int(len(pairs) * 0.8)
    trainset = [dspy.Example(source=p["source"], target=p["target"], label=p["label"]).with_inputs("source", "target") for p in pairs[:split]]
    valset = [dspy.Example(source=p["source"], target=p["target"], label=p["label"]).with_inputs("source", "target") for p in pairs[split:]]

    positives = sum(1 for p in pairs if p["label"] == "TRUE")
    print(f"Dataset: {len(pairs)} pares (TRUE={positives}, FALSE={len(pairs)-positives}) | Train={len(trainset)} Val={len(valset)}")

    baseline_f1 = compute_f1(TraceabilityClassifier(), valset)
    print(f"F1 baseline: {baseline_f1:.3f}")

    print("Optimizando zero-shot (modo medium)...")
    optimizer = dspy.MIPROv2(
        metric=f1_metric,
        auto="medium",
        num_threads=4,
        verbose=True,
    )
    optimized = optimizer.compile(
        TraceabilityClassifier(),
        trainset=trainset,
        max_bootstrapped_demos=0,
        max_labeled_demos=0,
    )

    optimized_f1 = compute_f1(optimized, valset)
    print(f"{'='*50}")
    print(f"Baseline:   {baseline_f1:.3f}")
    print(f"Optimizado: {optimized_f1:.3f} ({optimized_f1 - baseline_f1:+.3f})")
    print(f"{'='*50}")

    output_dir = HERE.parent / "experiments" / "dspy"
    output_dir.mkdir(parents=True, exist_ok=True)
    instruction = extract_instruction(optimized)
    with open(output_dir / "classification_optimized.txt", "w") as f:
        f.write(instruction.replace("\\n", "\n"))
    print(f"Guardado → {output_dir / 'classification_optimized.txt'}")


if __name__ == "__main__":
    main()
