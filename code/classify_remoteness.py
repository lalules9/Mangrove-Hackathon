"""
Official ABS Remoteness Area per LGA — as a classification, separate from the
area-weighted `stratum` and separate from Indigenous status.

    python classify_remoteness.py

Why this exists. `stratum` (in councils.csv) is the *sampling* stratum: it buckets each
LGA by the area-weighted mean of its SA2 remoteness scores, and it folds Indigenous
councils into one "indigenous" value. That is fine for drawing a stratified sample, but
it is not the ABS classification and it hides remoteness for the 17 Indigenous councils
(Cherbourg is Inner Regional; Aurukun is Very Remote — "indigenous" says neither).

This produces the ABS Remoteness Area instead. ADRI already carries the official RA of
every SA2 (`adri_sa2_QLD.csv`, `remoteness` column, sourced from the ASGS Remoteness
Structure). Each LGA is classified by the **modal RA of its SA2s** — the category most of
its SA2s sit in, which for nearly every LGA is where its population is. Ties break to the
less-remote category, because population concentrates in the town, not the hinterland.
The SA2 mix is written out so every call can be checked.

Output: data/qld_lga_remoteness.csv — joined in by build_master.py.
Indigenous status stays in its own column (`is_indigenous_council`); the two are
orthogonal and both belong on the map.
"""
from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent if ROOT.name == "code" else ROOT
DATA = BASE / "data"

# ADRI's remoteness name -> (rank, clean label). Rank 1 = least remote.
RA = {
    "Metropolitan":   (1, "Major City"),
    "Inner regional": (2, "Inner Regional"),
    "Outer regional": (3, "Outer Regional"),
    "Remote":         (4, "Remote"),
    "Very remote":    (5, "Very Remote"),
}
RANK_TO_LABEL = {rank: label for rank, label in RA.values()}


def key(name: str) -> str:
    """LGA name -> comparison key. Drops the ' (Qld)' the SA2 file appends."""
    return re.sub(r"[^a-z]", "", re.sub(r"\(qld\)", "", (name or "").lower()))


def main() -> None:
    sa2_path, councils_path = DATA / "adri_sa2_QLD.csv", DATA / "councils.csv"
    for p in (sa2_path, councils_path):
        if not p.exists():
            raise SystemExit(f"{p} not found — run fetch_adri.py / build_councils.py first.")

    sa2 = list(csv.DictReader(open(sa2_path, encoding="utf8")))
    councils = list(csv.DictReader(open(councils_path, encoding="utf8")))

    # LGA key -> list of official RA names, one per SA2 that falls in it
    ras_by_lga: dict[str, list[str]] = defaultdict(list)
    for s in sa2:
        for lga in (s.get("lga_names") or "").split(";"):
            ras_by_lga[key(lga)].append(s.get("remoteness", ""))

    rows, moved = [], []
    for c in sorted(councils, key=lambda r: r["short_name"]):
        ras = [r for r in ras_by_lga.get(key(c["short_name"]), []) if r in RA]
        if ras:
            counts = Counter(ras)
            # most common; tie -> lower rank (less remote)
            name, _ = min(counts.items(), key=lambda kv: (-kv[1], RA[kv[0]][0]))
            rank, label = RA[name]
            mix = "; ".join(f"{RA[k][1]}x{v}"
                            for k, v in sorted(counts.items(), key=lambda kv: RA[kv[0]][0]))
            method = "modal" if list(counts.values()).count(max(counts.values())) == 1 \
                     else "modal-tie-break"
        else:
            r = round(float(c.get("mean_remoteness_score") or 3))
            rank = min(5, max(1, r))
            label = RANK_TO_LABEL[rank]
            mix = f"(no SA2 match; area-weighted mean {c.get('mean_remoteness_score')})"
            method = "mean-fallback"

        stratum_as_ra = {"seq_metro": "Major City", "regional_city": "Inner Regional",
                         "outer_regional": "Outer Regional", "remote": "Remote",
                         "very_remote": "Very Remote"}.get(c["stratum"], "")
        changed = stratum_as_ra not in ("", label)
        if changed:
            moved.append((c["short_name"], c["stratum"], label, mix))

        rows.append({
            "short_name": c["short_name"],
            "remoteness_category": label,
            "remoteness_rank": rank,
            "is_indigenous_council": c["is_indigenous_council"],
            "remoteness_method": method,
            "remoteness_sa2_mix": mix,
            "differs_from_stratum": "True" if changed else "False",
        })

    out = DATA / "qld_lga_remoteness.csv"
    with open(out, "w", newline="", encoding="utf8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    dist = Counter(r["remoteness_category"] for r in rows)
    print(f"Wrote {out}  ({len(rows)} LGAs)")
    print("  distribution: " + ", ".join(f"{k} {v}" for k, v in
          sorted(dist.items(), key=lambda kv: [l for _, (rk, l) in RA.items()
                                               if l == kv[0]][0])))
    print(f"\n  {len(moved)} LGAs where the ABS category differs from the sampling stratum:")
    for name, st, label, mix in moved:
        print(f"    {name:20} {st:16} -> {label:16} [{mix}]")
    ind = [r for r in rows if r["is_indigenous_council"] in ("True", "true")]
    print(f"\n  {len(ind)} Indigenous councils now also carry a remoteness category, e.g.:")
    for r in ind[:6]:
        print(f"    {r['short_name']:20} {r['remoteness_category']}")
    print("\nATTRIBUTION")
    print("  Remoteness Areas from the ASGS Remoteness Structure, carried in the ADRI SA2")
    print("  data. Australian Bureau of Statistics / Natural Hazards Research Australia.")


if __name__ == "__main__":
    main()
