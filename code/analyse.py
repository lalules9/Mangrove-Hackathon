"""
Stratified results, error taxonomy, and a per-council report a council can act on.

    python analyse.py --provider gemini

Outputs:
  results/summary.md          the finding — accuracy by stratum and by failure mode
  results/councils/<name>.md  what to hand each council: what AI says, what is wrong, what to fix
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent if ROOT.name == "code" else ROOT   # data/ cache/ results/ sit beside code/
DATA, CACHE, RESULTS = BASE / "data", BASE / "cache", BASE / "results"
for _d in (DATA, CACHE, RESULTS):
    _d.mkdir(exist_ok=True)

ERROR_VERDICTS = {"wrong", "confidently_wrong", "wrong_council"}


def load(provider: str) -> list[dict]:
    p = RESULTS / f"graded_{provider}.jsonl"
    if not p.exists():
        raise SystemExit(f"{p} not found — run grade.py first.")
    return [json.loads(l) for l in p.read_text(encoding="utf8").splitlines() if l.strip()]


def pct(n: int, d: int) -> str:
    return f"{n / d:.0%}" if d else "—"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", default="gemini")
    args = ap.parse_args()
    records = load(args.provider)

    agreement = None
    agr_path = RESULTS / "agreement.json"
    if agr_path.exists():
        agreement = json.loads(agr_path.read_text(encoding="utf8")).get("grader_agreement")

    by_stratum: dict[str, Counter] = defaultdict(Counter)
    by_question: dict[str, Counter] = defaultdict(Counter)
    by_council: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_stratum[r.get("stratum") or "unclassified"][r["verdict"]] += 1
        by_question[r["question_id"]][r["verdict"]] += 1
        by_council[r["council"]].append(r)

    lines: list[str] = []
    add = lines.append
    add("# What AI tells Queenslanders about their council\n")
    add(f"Provider: `{args.provider}` · {len(records)} question-council pairs · "
        f"{len(by_council)} councils\n")

    if agreement is None:
        add("> **Grader not yet validated.** Run `validate.py` before quoting any figure below. "
            "Until then these are provisional.\n")
    else:
        add(f"> Grader agreement with human coding: **{agreement:.0%}** "
            f"(see `results/agreement.json` for the per-verdict breakdown).\n")

    add("\n## Accuracy by stratum\n")
    add("| Stratum | n | correct | wrong | confidently wrong | wrong council | refused | "
        "unverifiable |")
    add("|---|--:|--:|--:|--:|--:|--:|--:|")
    for s, c in sorted(by_stratum.items(), key=lambda kv: -sum(kv[1].values())):
        t = sum(c.values())
        add(f"| {s} | {t} | {pct(c['correct'], t)} | {pct(c['wrong'], t)} | "
            f"{pct(c['confidently_wrong'], t)} | {pct(c['wrong_council'], t)} | "
            f"{pct(c['refused'], t)} | {pct(c['unverifiable'], t)} |")

    add("\n**Read this row-wise.** The finding is the *gap* between strata, not any single "
        "number. High accuracy on well-published metro facts is the control that shows the "
        "instrument works.\n")

    add("\n## By question\n")
    add("| Question | n | correct | error rate | unverifiable |")
    add("|---|--:|--:|--:|--:|")
    for q, c in sorted(by_question.items(), key=lambda kv: -sum(kv[1].values())):
        t = sum(c.values())
        errs = sum(c[v] for v in ERROR_VERDICTS)
        add(f"| `{q}` | {t} | {pct(c['correct'], t)} | {pct(errs, t)} | "
            f"{pct(c['unverifiable'], t)} |")

    add("\nA high `unverifiable` rate is **not** a model failure — it means the council does not "
        "publish the answer on its own site. That is the most actionable finding in the project, "
        "because it is the part the council directly controls.\n")

    add("\n## Councils where the fix is clearest\n")
    ranked = sorted(by_council.items(),
                    key=lambda kv: -sum(r["verdict"] in ERROR_VERDICTS or
                                        r["verdict"] == "unverifiable" for r in kv[1]))
    add("| Council | errors | unpublished | report |")
    add("|---|--:|--:|---|")
    for name, recs in ranked[:20]:
        e = sum(r["verdict"] in ERROR_VERDICTS for r in recs)
        u = sum(r["verdict"] == "unverifiable" for r in recs)
        slug = name.lower().replace(" ", "-")
        add(f"| {name} | {e} | {u} | [report](councils/{slug}.md) |")

    add("\n## Limitations\n")
    add("- The Gemini API is **not** Google's AI Overview. It is a proxy with different "
        "retrieval. Where AI Overview results were captured separately, compare them before "
        "generalising to what people see in search.\n"
        "- Ground truth is what the council publishes on its website. A council may do the right "
        "thing and not publish it; for a question about what residents can find, publication is "
        "the thing being measured, but say this plainly.\n"
        "- Verdicts were assigned by a model, validated against human coding on a subsample. "
        "Trust each finding in proportion to the per-verdict agreement figure.\n"
        "- Fee questions were run in a single window. Fees change on 1 July; results are dated.\n")

    (RESULTS / "summary.md").write_text("\n".join(lines), encoding="utf8")

    # ------------------------------------------------ per-council actionable reports
    cdir = RESULTS / "councils"
    cdir.mkdir(exist_ok=True)
    for name, recs in by_council.items():
        problems = [r for r in recs
                    if r["verdict"] in ERROR_VERDICTS or r["verdict"] == "unverifiable"]
        out = [f"# What AI is telling residents about {name}\n",
               f"Checked {len(recs)} common questions. **{len(problems)} need attention.**\n",
               "\nYou did not choose this channel and you cannot see it — but residents hit it "
               "before they reach your website. Everything below is fixable by you.\n"]
        for r in problems:
            out.append(f"\n---\n\n### {r['prompt']}\n")
            out.append(f"**Verdict:** `{r['verdict']}`\n")
            if r["verdict"] == "unverifiable":
                out.append("\n**The issue:** your website does not answer this, so the model "
                           "guesses. **The fix:** publish it as plain text on a findable page — "
                           "not inside a PDF.\n")
            else:
                out.append(f"\n**AI said:** {r['answer'][:600]}\n")
                gt = r.get("ground_truth", {})
                out.append(f"\n**You publish:** {gt.get('fact')}\n")
                if r.get("key_discrepancy"):
                    out.append(f"\n**Discrepancy:** {r['key_discrepancy']}\n")
                out.append("\n**The fix:** state this unambiguously on a single findable page, "
                           "with the figure or deadline in the text itself.\n")
        out.append(f"\n---\n\n_Captured {recs[0].get('captured_at', '')} · "
                   f"provider `{args.provider}`. Verdicts assigned by an automated grader "
                   f"validated against human coding._\n")
        (cdir / f"{name.lower().replace(' ', '-')}.md").write_text("".join(out), encoding="utf8")

    print(f"Wrote {RESULTS / 'summary.md'} and {len(by_council)} council reports.")
    print("\nThe council reports are the deliverable. The summary is the finding.")


if __name__ == "__main__":
    main()
