"""
Pull the Australian Disaster Resilience Index and aggregate SA2 -> LGA.

    python fetch_adri.py                 # national
    python fetch_adri.py --state QLD     # just Queensland

The public site is an Angular app with no download button, but it is backed by a plain REST
API and the whole national dataset comes down in one request. No scraping, no automation of a
UI — the same endpoint the page itself calls on load.

    /adri/version            the two index versions (v1 = 2015, v2 = analysis year 2024)
    /sa2/<version_id>        every SA2 in Australia with all eight themes and both capacities
    /lga                     LGA reference list
    /resiliencenarratives    the official prose definition of each theme — use these verbatim

There is NO LGA-level endpoint (/lga/2 returns 404), so LGA scores have to be built here from
the SA2 records using the `lga_perc_covered` concordance the API helpfully ships inside each
record.

LICENCE — read this before you publish anything
    CC BY-NC 4.0. You may remix, adapt and build on it NON-COMMERCIALLY, and you must
    acknowledge Natural Hazards Research Australia (NHRA) as the author, preferably with
    their citation. A hackathon entry is non-commercial; attribute it anyway, on the page.
    Be polite to the API: this script caches, so it hits them once.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import httpx

BASE = "https://adri.naturalhazards.com.au"
ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent if ROOT.name == "code" else ROOT   # data/ cache/ results/ sit beside code/
DATA, CACHE, RESULTS = BASE / "data", BASE / "cache", BASE / "results"
for _d in (DATA, CACHE, RESULTS):
    _d.mkdir(exist_ok=True)

ATTRIBUTION = ("Australian Disaster Resilience Index, Natural Hazards Research Australia / "
               "University of New England. Licensed CC BY-NC 4.0.")

# The eight themes, exactly as the API names them.
THEMES = ["social_character", "economic_capital", "planning_build_environment",
          "emergency_services", "information_access", "govt_leadership",
          "community_social_engagement", "community_capital"]
CAPACITIES = ["coping_capacity", "adaptive_capacity", "andri"]


def get(path: str) -> list | dict:
    """Fetch once, cache to disk, never re-hit their server."""
    cache_file = CACHE / f"adri_{path.strip('/').replace('/', '_')}.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf8"))
    r = httpx.get(f"{BASE}{path}", timeout=180,
                  headers={"User-Agent": "hackathon-research/0.1 (non-commercial)"})
    r.raise_for_status()
    data = r.json()
    cache_file.write_text(json.dumps(data), encoding="utf8")
    print(f"  fetched {path} -> {cache_file.name}")
    return data


def to_float(v) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def aggregate_to_lga(sa2_rows: list[dict]) -> list[dict]:
    """
    Roll SA2 scores up to LGA, weighting each SA2's contribution by
    (its area) x (the share of that SA2 inside the LGA).

    CAVEAT worth stating in your write-up: area weighting over-weights large empty SA2s and
    under-weights dense urban ones. Population weighting is better — join ABS ERP by SA2 code
    and swap `weight` below. The ERP fields in this payload are null, which is why area is
    used here.
    """
    buckets: dict[tuple, dict] = defaultdict(
        lambda: {"w": 0.0, "sums": defaultdict(float), "sa2s": 0,
                 "remoteness_w": 0.0, "worst_remoteness": 0})

    for r in sa2_rows:
        area = to_float(r.get("area_sqkm")) or 0.0
        for cov in (r.get("lga_perc_covered") or []):
            share = (cov.get("perc_covered") or 0) / 100.0
            if share <= 0:
                continue
            weight = max(area * share, 1e-9)
            key = (r["state_name"], cov["lga_id"], cov["lga_name"])
            b = buckets[key]
            b["w"] += weight
            b["sa2s"] += 1
            b["remoteness_w"] += (r.get("remoteness_score") or 0) * weight
            b["worst_remoteness"] = max(b["worst_remoteness"], r.get("remoteness_score") or 0)
            for f in THEMES + CAPACITIES:
                v = to_float(r.get(f))
                if v is not None:
                    b["sums"][f] += v * weight

    out = []
    for (state, lga_id, lga_name), b in buckets.items():
        if b["w"] <= 0:
            continue
        row = {"state": state, "lga_id": lga_id, "lga_name": lga_name,
               "sa2_count": b["sa2s"],
               "mean_remoteness_score": round(b["remoteness_w"] / b["w"], 3),
               "worst_remoteness_score": b["worst_remoteness"]}
        for f in CAPACITIES + THEMES:
            row[f] = round(b["sums"][f] / b["w"], 4)
        out.append(row)
    return sorted(out, key=lambda r: (r["state"], r["lga_name"]))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", help="filter to one state, e.g. QLD")
    ap.add_argument("--version", type=int, default=2, help="ADRI version id (2 = 2024)")
    args = ap.parse_args()

    print("Versions available:")
    for v in get("/adri/version"):
        print(f"  id={v['id']}  {v['description']}  year={v['year']}")

    print(f"\nFetching SA2 records for version {args.version}...")
    sa2 = get(f"/sa2/{args.version}")
    print(f"  {len(sa2)} SA2 records nationally")

    if args.state:
        sa2 = [r for r in sa2 if r.get("state_name") == args.state.upper()]
        print(f"  {len(sa2)} in {args.state.upper()}")

    suffix = f"_{args.state.upper()}" if args.state else ""

    # --- SA2 level, geometry stripped (the geom blob is enormous and you don't need it) ---
    sa2_cols = (["sa2_code", "sa2_name", "state_name", "remoteness", "remoteness_score",
                 "analysis_year", "sa4_name", "gccsa_name"] + CAPACITIES + THEMES
                + ["andri_quartile", "coping_capacity_quartile", "adaptive_capacity_quartile",
                   "lga_names"])
    sa2_path = DATA / f"adri_sa2{suffix}.csv"
    with open(sa2_path, "w", newline="", encoding="utf8") as f:
        w = csv.DictWriter(f, fieldnames=sa2_cols, extrasaction="ignore")
        w.writeheader()
        for r in sa2:
            w.writerow({**r, "lga_names": "; ".join(
                l["lga_name"] for l in (r.get("lga_perc_covered") or []))})
    print(f"\nWrote {sa2_path}  ({len(sa2)} rows)")

    # --- LGA level, aggregated here because the API has no LGA endpoint ---
    lga_rows = aggregate_to_lga(sa2)
    lga_path = DATA / f"adri_lga{suffix}.csv"
    with open(lga_path, "w", newline="", encoding="utf8") as f:
        w = csv.DictWriter(f, fieldnames=list(lga_rows[0].keys()))
        w.writeheader()
        w.writerows(lga_rows)
    print(f"Wrote {lga_path}  ({len(lga_rows)} LGAs)")

    # --- the official theme definitions, for your rubric wording ---
    narr = get("/resiliencenarratives")
    narr_path = DATA / "adri_theme_definitions.json"
    narr_path.write_text(json.dumps(narr, indent=2), encoding="utf8")
    print(f"Wrote {narr_path}  ({len(narr)} theme definitions — quote these verbatim)")

    (DATA / "adri_ATTRIBUTION.txt").write_text(ATTRIBUTION + "\n", encoding="utf8")

    # --- a look at the distribution, so you know what you have ---
    ranked = sorted((r for r in lga_rows if r["andri"] > 0), key=lambda r: r["andri"])
    print(f"\nLowest ANDRI (least resilient) — {args.state.upper() if args.state else 'national'}:")
    for r in ranked[:8]:
        print(f"  {r['andri']:.4f}  {r['lga_name']:32} "
              f"coping={r['coping_capacity']:.3f} adaptive={r['adaptive_capacity']:.3f} "
              f"remoteness={r['mean_remoteness_score']:.1f}")
    print("\nHighest ANDRI (most resilient):")
    for r in ranked[-4:][::-1]:
        print(f"  {r['andri']:.4f}  {r['lga_name']:32} "
              f"coping={r['coping_capacity']:.3f} adaptive={r['adaptive_capacity']:.3f} "
              f"remoteness={r['mean_remoteness_score']:.1f}")

    zeros = [r for r in lga_rows if r["andri"] == 0]
    if zeros:
        print(f"\nNOTE: {len(zeros)} LGA(s) score exactly 0.0000 — "
              f"{', '.join(r['lga_name'] for r in zeros[:5])}")
        print("  The index looks min-max normalised, so 0 is the floor of the scale, NOT an")
        print("  absolute absence of resilience. Do not report it as though it were.")

    print(f"\n{ATTRIBUTION}")


if __name__ == "__main__":
    main()
