"""
Grade model answers against ground truth taken from each council's own website.

    python grade.py --provider gemini

Two stages, both cached:
  1. Ground truth  — fetch the council's own page and extract the fact. Written to
                     data/ground_truth.json for you to SPOT-CHECK BY HAND. Where the council
                     does not publish it, the verdict is `unverifiable`, which is a finding
                     about the council, not an error by the model.
  2. Grading       — compare the model answer to that ground truth.

This grader is itself a model. It is not evidence until validate.py has measured its agreement
with your hand labels. Run that before you believe any number this produces.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path

import httpx
import yaml
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent if ROOT.name == "code" else ROOT   # data/ cache/ results/ sit beside code/
DATA, CACHE, RESULTS = BASE / "data", BASE / "cache", BASE / "results"
for _d in (DATA, CACHE, RESULTS):
    _d.mkdir(exist_ok=True)

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
GRADER_MODEL = os.getenv("GRADER_MODEL", "claude-sonnet-5")

VERDICTS = ["correct", "wrong", "confidently_wrong", "wrong_council",
            "refused", "unverifiable"]


def h(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:20]


def load_questions() -> dict[str, dict]:
    qs = yaml.safe_load((ROOT / "questions.yaml").read_text(encoding="utf8"))["questions"]
    return {q["id"]: q for q in qs}


def strip_html(html: str) -> str:
    html = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", text).strip()


def fetch_council_pages(base_url: str, hint: str, limit: int = 4) -> str:
    """Fetch the homepage plus a few pages whose link text matches the hint terms."""
    chunks: list[str] = []
    terms = [t for t in re.split(r"[^a-z]+", hint.lower()) if len(t) > 3]
    try:
        with httpx.Client(timeout=25, follow_redirects=True,
                          headers={"User-Agent": "council-ai-audit/0.1 (hackathon research)"}) as c:
            home = c.get(base_url)
            chunks.append(strip_html(home.text)[:4000])
            links = re.findall(r'href="([^"]+)"[^>]*>([^<]{3,80})<', home.text, flags=re.I)
            scored = []
            for href, label in links:
                score = sum(t in (href + " " + label).lower() for t in terms)
                if score:
                    scored.append((score, httpx.URL(str(home.url)).join(href)))
            scored.sort(key=lambda x: -x[0])
            seen: set[str] = set()
            for _, url in scored:
                s = str(url)
                if s in seen or not s.startswith(("http://", "https://")):
                    continue
                seen.add(s)
                try:
                    chunks.append(f"\n--- {s} ---\n" + strip_html(c.get(s).text)[:6000])
                except Exception:
                    pass
                if len(seen) >= limit:
                    break
    except Exception as e:
        chunks.append(f"[fetch failed: {e}]")
    return "\n".join(chunks)[:24000]


def ask_claude(prompt: str, max_tokens: int = 900) -> str:
    resp = client.messages.create(
        model=GRADER_MODEL, max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}])
    return "".join(b.text for b in resp.content if b.type == "text")


def extract_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, flags=re.S)
    return json.loads(m.group(0)) if m else {}


def get_ground_truth(council: str, url: str, q: dict, store: dict) -> dict:
    k = h(council, q["id"])
    if k in store:
        return store[k]
    page_text = fetch_council_pages(url, q["ground_truth_hint"])
    prompt = f"""You are establishing ground truth from a council's own website.

COUNCIL: {council}
QUESTION: {q['text'].format(council=council)}

WEBSITE CONTENT:
{page_text}

Extract only what this council itself publishes. Do not use outside knowledge. If the content
does not answer the question, say so plainly — "not published" is a valid and useful result.

Return JSON only:
{{"published": true|false,
  "fact": "the council's own answer, quoted or closely paraphrased, or null",
  "evidence_quote": "a short verbatim quote from the page, or null",
  "confidence": "high"|"medium"|"low",
  "note": "anything ambiguous a human should check"}}"""
    gt = extract_json(ask_claude(prompt))
    gt["_council"], gt["_question_id"] = council, q["id"]
    store[k] = gt
    return gt


def grade_one(rec: dict, q: dict, gt: dict) -> dict:
    if not gt.get("published"):
        return {"verdict": "unverifiable", "reasoning": "Council does not publish this.",
                "grader_confidence": "high"}
    prompt = f"""Grade an AI assistant's answer about an Australian local council against the
council's own published information.

COUNCIL: {rec['council']}
QUESTION: {rec['prompt']}

COUNCIL'S PUBLISHED POSITION (ground truth):
{gt.get('fact')}
Evidence: {gt.get('evidence_quote')}

AI ASSISTANT'S ANSWER:
{rec['answer']}

Choose exactly one verdict:
- correct: matches the council's published information
- wrong: contradicts it
- confidently_wrong: contradicts it AND asserts it without hedging or caveat
- wrong_council: describes a different council's process, or a generic state/national answer
  presented as this council's
- refused: declined to answer or said it did not know (a safe failure, not an error)

Judge substance, not wording. A correct answer phrased differently is correct. An answer that
hedges appropriately and is right is correct, not refused.

Return JSON only:
{{"verdict": "...",
  "reasoning": "one sentence",
  "grader_confidence": "high"|"medium"|"low",
  "key_discrepancy": "what specifically differs, or null"}}"""
    out = extract_json(ask_claude(prompt))
    if out.get("verdict") not in VERDICTS:
        out = {"verdict": "wrong", "reasoning": f"unparsable grader output: {out}",
               "grader_confidence": "low"}
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", default="gemini")
    ap.add_argument("--limit", type=int, help="grade only the first N (for a smoke test)")
    args = ap.parse_args()

    questions = load_questions()
    gt_path = DATA / "ground_truth.json"
    store = json.loads(gt_path.read_text(encoding="utf8")) if gt_path.exists() else {}

    src = RESULTS / f"responses_{args.provider}.jsonl"
    if not src.exists():
        raise SystemExit(f"{src} not found — run run_queries.py first.")
    records = [json.loads(l) for l in src.read_text(encoding="utf8").splitlines() if l.strip()]
    if args.limit:
        records = records[: args.limit]

    out_path = RESULTS / f"graded_{args.provider}.jsonl"
    with open(out_path, "w", encoding="utf8") as out:
        for i, rec in enumerate(records, 1):
            q = questions[rec["question_id"]]
            gt = get_ground_truth(rec["council"], rec["council_url"], q, store)
            verdict = grade_one(rec, q, gt)
            out.write(json.dumps({**rec, "ground_truth": gt, **verdict},
                                 ensure_ascii=False) + "\n")
            print(f"  [{i}/{len(records)}] {rec['council'][:34]:34} "
                  f"{rec['question_id']:16} -> {verdict['verdict']}")
            if i % 20 == 0:
                gt_path.write_text(json.dumps(store, ensure_ascii=False, indent=2),
                                   encoding="utf8")

    gt_path.write_text(json.dumps(store, ensure_ascii=False, indent=2), encoding="utf8")
    print(f"\nGraded -> {out_path}")
    print("NEXT: spot-check data/ground_truth.json by hand, then run validate.py.")
    print("These numbers are not evidence until the grader has been validated.")


if __name__ == "__main__":
    main()
