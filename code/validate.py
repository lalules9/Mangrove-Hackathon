"""
Hand-label a subsample, then measure agreement. This is the methodological spine of the project.

    python validate.py --rater paul  --n 60     # each of you does this INDEPENDENTLY
    python validate.py --rater julie --n 60     # same sample, same seed, no conferring
    python validate.py --report                 # inter-rater + grader agreement

Why it matters: you are using a model to grade a model. Until you have measured this grader
against human judgement, every accuracy figure in the project is unverified. Report the number
even when it is bad — especially when it is bad, and per failure type, because a grader that is
reliable on `correct` and unreliable on `confidently_wrong` tells you which findings to trust.
"""
from __future__ import annotations

import argparse
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent if ROOT.name == "code" else ROOT   # data/ cache/ results/ sit beside code/
DATA, CACHE, RESULTS = BASE / "data", BASE / "cache", BASE / "results"
for _d in (DATA, CACHE, RESULTS):
    _d.mkdir(exist_ok=True)

VERDICTS = ["correct", "wrong", "confidently_wrong", "wrong_council",
            "refused", "unverifiable"]


def load_graded(provider: str) -> list[dict]:
    p = RESULTS / f"graded_{provider}.jsonl"
    if not p.exists():
        raise SystemExit(f"{p} not found — run grade.py first.")
    return [json.loads(l) for l in p.read_text(encoding="utf8").splitlines() if l.strip()]


def sample(records: list[dict], n: int, seed: int) -> list[dict]:
    """Same seed gives both raters the same items. Stratified so rare verdicts get seen."""
    random.seed(seed)
    by_verdict: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_verdict[r["verdict"]].append(r)
    per = max(1, n // max(1, len(by_verdict)))
    out: list[dict] = []
    for group in by_verdict.values():
        out.extend(random.sample(group, min(per, len(group))))
    random.shuffle(out)
    return out[:n]


def label(args) -> None:
    records = load_graded(args.provider)
    items = sample(records, args.n, args.seed)
    path = RESULTS / f"labels_{args.rater}.json"
    done = json.loads(path.read_text(encoding="utf8")) if path.exists() else {}

    print(f"\n{len(items)} items. You will NOT see the grader's verdict — that is deliberate.")
    print(f"Verdicts: {', '.join(f'{i+1}={v}' for i, v in enumerate(VERDICTS))}")
    print("Enter s to skip, q to save and quit.\n")

    for i, rec in enumerate(items, 1):
        k = f"{rec['council']}|{rec['question_id']}"
        if k in done:
            continue
        print("=" * 78)
        print(f"[{i}/{len(items)}]  {rec['council']}  —  {rec['question_id']}")
        print(f"\nQ: {rec['prompt']}")
        gt = rec.get("ground_truth", {})
        print(f"\nCOUNCIL PUBLISHES: {gt.get('fact') if gt.get('published') else '[NOT PUBLISHED]'}")
        if gt.get("evidence_quote"):
            print(f"  evidence: \"{gt['evidence_quote'][:220]}\"")
        print(f"\nAI ANSWER:\n{rec['answer'][:1100]}")
        print()
        while True:
            choice = input("verdict 1-6 / s / q > ").strip().lower()
            if choice == "q":
                path.write_text(json.dumps(done, indent=2), encoding="utf8")
                print(f"Saved {len(done)} labels -> {path}")
                return
            if choice == "s":
                break
            if choice.isdigit() and 1 <= int(choice) <= len(VERDICTS):
                done[k] = VERDICTS[int(choice) - 1]
                break
            print("  1-6, s, or q")

    path.write_text(json.dumps(done, indent=2), encoding="utf8")
    print(f"\nSaved {len(done)} labels -> {path}")


def report(args) -> None:
    records = {f"{r['council']}|{r['question_id']}": r for r in load_graded(args.provider)}
    raters = {}
    for p in RESULTS.glob("labels_*.json"):
        raters[p.stem.replace("labels_", "")] = json.loads(p.read_text(encoding="utf8"))
    if not raters:
        raise SystemExit("No label files found. Run --rater <name> first.")

    print(f"\nRaters: {', '.join(raters)}")

    # --- inter-rater agreement -------------------------------------------------
    names = sorted(raters)
    if len(names) >= 2:
        a, b = raters[names[0]], raters[names[1]]
        shared = sorted(set(a) & set(b))
        agree = sum(a[k] == b[k] for k in shared)
        print(f"\nINTER-RATER ({names[0]} vs {names[1]}) on {len(shared)} shared items")
        print(f"  raw agreement: {agree}/{len(shared)} = {agree / max(1, len(shared)):.1%}")
        disagreements = [(k, a[k], b[k]) for k in shared if a[k] != b[k]]
        if disagreements:
            print("  disagreements — these show where your categories are fuzzy:")
            for k, va, vb in disagreements[:12]:
                print(f"    {k[:52]:52} {va} / {vb}")
        print("\n  If this is below ~80%, your verdict definitions need tightening before")
        print("  you trust the grader numbers. Fix the rubric, re-label, say so in the writeup.")
        consensus = {k: a[k] for k in shared if a[k] == b[k]}
    else:
        consensus = dict(next(iter(raters.values())))
        print("\nOnly one rater — report this as a limitation; you have no inter-rater number.")

    # --- grader vs human -------------------------------------------------------
    print(f"\nGRADER vs HUMAN on {len(consensus)} agreed items")
    hits = Counter()
    per_type: dict[str, list[bool]] = defaultdict(list)
    confusion: Counter = Counter()
    for k, human in consensus.items():
        rec = records.get(k)
        if not rec:
            continue
        ok = rec["verdict"] == human
        hits[ok] += 1
        per_type[human].append(ok)
        if not ok:
            confusion[(human, rec["verdict"])] += 1

    total = hits[True] + hits[False]
    if total:
        print(f"  overall agreement: {hits[True]}/{total} = {hits[True] / total:.1%}")
        print("\n  by human verdict (this is the number to quote per finding):")
        for v in VERDICTS:
            vals = per_type.get(v, [])
            if vals:
                print(f"    {v:20} {sum(vals):3}/{len(vals):3} = {sum(vals) / len(vals):.0%}")
        if confusion:
            print("\n  most common grader errors (human -> grader):")
            for (hv, gv), n in confusion.most_common(8):
                print(f"    {hv:20} -> {gv:20} x{n}")

    out = RESULTS / "agreement.json"
    out.write_text(json.dumps({
        "n_consensus": len(consensus),
        "grader_agreement": (hits[True] / total) if total else None,
        "by_verdict": {v: (sum(x) / len(x)) for v, x in per_type.items() if x},
    }, indent=2), encoding="utf8")
    print(f"\nWrote {out} — put this number on a slide.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", default="gemini")
    ap.add_argument("--rater", help="your name — label mode")
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--seed", type=int, default=17, help="MUST match between raters")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    report(a) if a.report else label(a)
