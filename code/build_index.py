"""
Score every Queensland LGA against the formula in config/index.yaml.

    python build_index.py

Reads   data/qld_lga_master.csv  and  config/index.yaml
Writes  data/qld_lga_index.csv   — the file the map consumes

The formula lives entirely in the YAML. This script only executes it: normalise each input to
0–1 where 1 means more at risk, apply the stated direction, weight, sum, rank. Change nothing
here to change the index.

It also runs the honesty check: correlation and rank shift against ADRI, which is held out of
the model. If the rank correlation is very high you have rebuilt the natural-hazard index with
extra steps, and that is worth knowing before anything is built on top.
"""
from __future__ import annotations

import csv
import statistics as st
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent if ROOT.name == "code" else ROOT
DATA, CONFIG = BASE / "data", BASE / "config"

TRUE = {"true", "yes", "1", "y"}
FALSE = {"false", "no", "0", "n"}


def num(v):
    try:
        return float(str(v).replace(",", "").replace("$", ""))
    except (TypeError, ValueError):
        return None


def boolean(v):
    s = str(v).strip().lower()
    return True if s in TRUE else False if s in FALSE else None


def normalise(vals: list[float], method: str) -> list[float]:
    """Map to 0–1. Callers handle direction; this only rescales."""
    present = [v for v in vals if v is not None]
    if not present:
        return [None] * len(vals)
    if method == "percentile":
        order = sorted(present)
        n = len(order)
        return [None if v is None else
                (sum(1 for o in order if o < v) + 0.5 * sum(1 for o in order if o == v)) / n
                for v in vals]
    if method == "zscore_clip":
        m, sd = st.mean(present), (st.pstdev(present) or 1.0)
        z = [None if v is None else max(-2.5, min(2.5, (v - m) / sd)) for v in vals]
        return [None if v is None else (v + 2.5) / 5.0 for v in z]
    lo, hi = min(present), max(present)          # minmax
    rng = (hi - lo) or 1.0
    return [None if v is None else (v - lo) / rng for v in vals]


def main() -> None:
    cfg = yaml.safe_load((CONFIG / "index.yaml").read_text(encoding="utf8"))
    rows = list(csv.DictReader(open(DATA / "qld_lga_master.csv", encoding="utf8")))
    held_out = set(cfg["meta"].get("held_out", []))
    default_norm = cfg["meta"].get("normalise_default", "percentile")

    print(f"{cfg['meta']['name']}  v{cfg['meta']['version']}")
    print(f"{len(rows)} LGAs | {len(held_out)} columns held out\n")

    # ---- normalise every input, honouring direction ---------------------------------
    norm_vals: dict[str, list] = {}
    for cname, comp in cfg["components"].items():
        for inp in comp["inputs"]:
            col, dirn = inp["col"], inp["direction"]
            if col in held_out:
                raise SystemExit(f"REFUSED: '{col}' is held out and cannot be scored.")
            if col not in rows[0]:
                raise SystemExit(f"Column '{col}' not in master file.")
            if dirn in ("true_worse", "false_worse"):
                want = dirn == "true_worse"
                vals = [None if boolean(r[col]) is None
                        else (1.0 if boolean(r[col]) is want else 0.0) for r in rows]
            else:
                raw = [num(r[col]) for r in rows]
                vals = normalise(raw, inp.get("normalise", default_norm))
                if dirn == "invert":
                    vals = [None if v is None else 1.0 - v for v in vals]
            norm_vals[col] = vals
            n = sum(1 for v in vals if v is not None)
            print(f"  {cname:26} {col:32} {dirn:13} {n:>3}/{len(rows)}")

    # ---- score ----------------------------------------------------------------------
    out = []
    for i, r in enumerate(rows):
        rec = {k: r.get(k, "") for k in (
            "short_name", "council_name", "stratum", "abs_lga_code",
            "is_indigenous_council", "population_latest",
            "remoteness_category", "remoteness_rank")}
        total, complete = 0.0, 0
        for cname, comp in cfg["components"].items():
            got = [(inp, norm_vals[inp["col"]][i]) for inp in comp["inputs"]]
            avail = [(inp, v) for inp, v in got if v is not None]
            # Always write the same keys for every row, whether or not this component has
            # data for this LGA -- otherwise csv.DictWriter breaks the moment row 0 happens
            # to be a council with no available inputs (fieldnames come from out[0] only).
            rec[f"{cname}_inputs_used"] = f"{len(avail)}/{len(got)}"
            for inp, v in got:
                rec[f"n_{inp['col']}"] = "" if v is None else round(v, 4)
            if not avail:
                rec[f"{cname}_score"] = ""
                continue
            wsum = sum(inp["weight"] for inp, _ in avail)      # renormalise on missing
            score = sum(v * inp["weight"] for inp, v in avail) / wsum
            rec[f"{cname}_score"] = round(score, 4)
            total += score * comp["weight"]
            complete += len(avail) == len(got)
        rec["ai_risk_index"] = round(total, 4)
        rec["components_complete"] = f"{complete}/{len(cfg['components'])}"
        rec["adri_andri"] = r.get("adri_andri", "")
        out.append(rec)

    # ---- rank, and compare against the held-out control ------------------------------
    for key, field in (("ai_risk_index", "ai_risk_rank"), ("adri_andri", "adri_rank")):
        rev = key == "ai_risk_index"          # 1 = most at risk / least resilient
        vals = [(i, num(rec[key])) for i, rec in enumerate(out) if num(rec[key]) is not None]
        vals.sort(key=lambda x: -x[1] if rev else x[1])
        for rank, (i, _) in enumerate(vals, 1):
            out[i][field] = rank
    for rec in out:
        a, b = rec.get("ai_risk_rank"), rec.get("adri_rank")
        rec["rank_shift"] = (b - a) if isinstance(a, int) and isinstance(b, int) else ""

    # Written twice: data/ is the record, docs/map/ is what the map fetches. Keeping the
    # copy here stops the two drifting (they had).
    targets = [DATA / "qld_lga_index.csv"]
    map_dir = BASE / "docs" / "map"
    if map_dir.is_dir():
        targets.append(map_dir / "qld_lga_index.csv")
    for path in targets:
        with open(path, "w", newline="", encoding="utf8") as f:
            w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
            w.writeheader()
            w.writerows(out)
        print(f"\nWrote {path}  ({len(out)} rows x {len(out[0])} cols)")

    # ---- the honesty check -----------------------------------------------------------
    pairs = [(num(r["ai_risk_index"]), num(r["adri_andri"])) for r in out
             if num(r["ai_risk_index"]) is not None and num(r["adri_andri"]) is not None]
    xs, ys = zip(*pairs)
    r_pearson = st.correlation(xs, ys)
    rx = {i: k for k, i in enumerate(sorted(range(len(xs)), key=lambda j: xs[j]))}
    ry = {i: k for k, i in enumerate(sorted(range(len(ys)), key=lambda j: ys[j]))}
    r_spear = st.correlation([rx[i] for i in range(len(xs))], [ry[i] for i in range(len(ys))])

    print(f"\n{'='*66}\nAGAINST THE HELD-OUT CONTROL (ADRI ANDRI), n={len(pairs)}")
    print(f"  Pearson  r = {r_pearson:+.3f}")
    print(f"  Spearman r = {r_spear:+.3f}   (expected negative: high risk = low resilience)")
    if abs(r_spear) > 0.9:
        print("  -> Near-identical. You have rebuilt ADRI. Report that as the finding.")
    elif abs(r_spear) > 0.7:
        print("  -> Strongly related but not identical. The divergence is the finding.")
    else:
        print("  -> Substantially different. Explain WHY before anyone else asks.")

    print(f"\n  Most AT RISK on our index:")
    for rec in sorted(out, key=lambda r: r.get("ai_risk_rank") or 999)[:8]:
        print(f"    {rec['ai_risk_rank']:>3}. {rec['short_name'][:24]:24} "
              f"index={rec['ai_risk_index']:.3f}  adri_rank={rec.get('adri_rank','')}"
              f"  shift={rec.get('rank_shift','')}")

    shifted = [r for r in out if isinstance(r.get("rank_shift"), int)]
    print(f"\n  Biggest DIVERGENCE — worse on ours than ADRI predicts:")
    for rec in sorted(shifted, key=lambda r: -r["rank_shift"])[:6]:
        print(f"    {rec['short_name'][:24]:24} ours #{rec['ai_risk_rank']:<3} "
              f"adri #{rec['adri_rank']:<3}  shift +{rec['rank_shift']}")


if __name__ == "__main__":
    main()
