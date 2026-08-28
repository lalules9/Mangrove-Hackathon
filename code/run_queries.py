"""
Run the question set against one or more providers, caching and archiving everything.

    python run_queries.py --provider gemini              # full sweep, reproducible spine
    python run_queries.py --provider serp --sample 25    # real AI Overviews, stratified subsample

Every response is cached by (provider, council, question) so re-runs are free, and archived with
a timestamp so you can prove what a model said on a given day. Never delete archive/.

On providers:
  gemini  Gemini API. Cheap, scriptable, reproducible. NOT the same system as Google's AI
          Overview — different retrieval. It is a proxy. Say so in the write-up.
  serp    A SERP API that returns the AI Overview block as structured data. This is the
          legitimate way to capture what people actually see; the service does the querying.
          Set SERP_PROVIDER and SERP_API_KEY in .env.

Do not add a provider that scripts google.com directly.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
import yaml
from dotenv import load_dotenv

load_dotenv()
ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent if ROOT.name == "code" else ROOT   # data/ cache/ results/ sit beside code/
DATA, CACHE, RESULTS = BASE / "data", BASE / "cache", BASE / "results"
for _d in (DATA, CACHE, RESULTS):
    _d.mkdir(exist_ok=True)
ARCHIVE = BASE / "archive"
ARCHIVE.mkdir(exist_ok=True)


def key(provider: str, council: str, qid: str) -> str:
    return hashlib.sha256(f"{provider}|{council}|{qid}".encode()).hexdigest()[:20]


def load_questions() -> list[dict]:
    return yaml.safe_load((ROOT / "questions.yaml").read_text(encoding="utf8"))["questions"]


def load_councils() -> list[dict]:
    path = DATA / "councils.csv"
    if not path.exists():
        raise SystemExit("Run build_councils.py --verify first.")
    with open(path, encoding="utf8") as f:
        rows = [r for r in csv.DictReader(f) if r.get("website")]
    if not rows:
        raise SystemExit("No councils with verified websites. Fix data/councils.csv.")
    return rows


# ----------------------------------------------------------------------------- providers

def ask_gemini(prompt: str) -> dict:
    api_key = os.environ["GEMINI_API_KEY"]
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    r = httpx.post(url, params={"key": api_key},
                   json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=90)
    r.raise_for_status()
    body = r.json()
    try:
        text = body["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        text = ""
    return {"text": text, "raw": body, "model": model}


def ask_serp(prompt: str) -> dict:
    """
    Fetch the AI Overview for a real Google search via a SERP API.

    Configure in .env:
        SERP_PROVIDER=serper        (or serpapi, dataforseo)
        SERP_API_KEY=...
    Response shapes differ between providers — print `raw` once and adjust the extraction.
    """
    provider = os.getenv("SERP_PROVIDER", "serper").lower()
    api_key = os.environ["SERP_API_KEY"]

    if provider == "serper":
        r = httpx.post("https://google.serper.dev/search",
                       headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
                       json={"q": prompt, "gl": "au", "hl": "en"}, timeout=90)
        r.raise_for_status()
        body = r.json()
        text = (body.get("answerBox", {}) or {}).get("answer") \
            or (body.get("answerBox", {}) or {}).get("snippet") \
            or (body.get("aiOverview", {}) or {}).get("text", "")
    elif provider == "serpapi":
        r = httpx.get("https://serpapi.com/search",
                      params={"q": prompt, "gl": "au", "hl": "en", "api_key": api_key},
                      timeout=90)
        r.raise_for_status()
        body = r.json()
        ov = body.get("ai_overview", {}) or {}
        text = "\n".join(b.get("snippet", "") for b in ov.get("text_blocks", [])) or ov.get("text", "")
    else:
        raise SystemExit(f"Unknown SERP_PROVIDER={provider}. Add its shape to ask_serp().")

    if not text:
        text = "[NO AI OVERVIEW RETURNED — record as such, this is itself data]"
    return {"text": text, "raw": body, "model": f"serp:{provider}"}


PROVIDERS = {"gemini": ask_gemini, "serp": ask_serp}


# ----------------------------------------------------------------------------- runner

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", required=True, choices=sorted(PROVIDERS))
    ap.add_argument("--sample", type=int, help="stratified subsample of N councils")
    ap.add_argument("--seed", type=int, default=17, help="sampling seed — record it")
    ap.add_argument("--sleep", type=float, default=1.0, help="seconds between live calls")
    args = ap.parse_args()

    questions, councils = load_questions(), load_councils()

    if args.sample and args.sample < len(councils):
        random.seed(args.seed)
        by_stratum: dict[str, list[dict]] = {}
        for c in councils:
            by_stratum.setdefault(c.get("stratum", "unclassified"), []).append(c)
        per = max(1, args.sample // max(1, len(by_stratum)))
        councils = [c for group in by_stratum.values()
                    for c in random.sample(group, min(per, len(group)))]
        print(f"Stratified subsample: {len(councils)} councils (seed={args.seed})")

    ask = PROVIDERS[args.provider]
    out_path = ROOT / "results" / f"responses_{args.provider}.jsonl"
    out_path.parent.mkdir(exist_ok=True)

    total = len(councils) * len(questions)
    done = hits = 0
    with open(out_path, "w", encoding="utf8") as out:
        for council in councils:
            for q in questions:
                done += 1
                k = key(args.provider, council["name"], q["id"])
                cache_file = CACHE / f"{k}.json"
                prompt = q["text"].format(council=council["name"])

                if cache_file.exists():
                    rec = json.loads(cache_file.read_text(encoding="utf8"))
                    hits += 1
                else:
                    try:
                        resp = ask(prompt)
                    except Exception as e:
                        print(f"  [{done}/{total}] ERROR {council['name']} / {q['id']}: {e}")
                        continue
                    rec = {
                        "provider": args.provider, "model": resp["model"],
                        "council": council["name"], "council_url": council["website"],
                        "stratum": council.get("stratum", ""), "question_id": q["id"],
                        "failure_modes": q["failure_modes"], "prompt": prompt,
                        "answer": resp["text"],
                        "captured_at": datetime.now(timezone.utc).isoformat(),
                    }
                    cache_file.write_text(json.dumps(rec, ensure_ascii=False, indent=2),
                                          encoding="utf8")
                    # Archive the untouched provider payload — this is the evidence trail.
                    (ARCHIVE / f"{k}_raw.json").write_text(
                        json.dumps(resp["raw"], ensure_ascii=False, indent=2), encoding="utf8")
                    time.sleep(args.sleep)

                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                if done % 25 == 0:
                    print(f"  [{done}/{total}] cached={hits}")

    print(f"\nWrote {done} responses to {out_path} ({hits} from cache).")
    print(f"Raw payloads archived in {ARCHIVE}/ — do not delete, this is your proof.")


if __name__ == "__main__":
    main()
