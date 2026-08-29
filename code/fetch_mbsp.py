"""
Mobile Black Spot Program — funded base stations, per Queensland LGA.

    python fetch_mbsp.py

Source: Department of Infrastructure, Transport, Regional Development, Communications,
Sport and the Arts — "Mobile Black Spot Program (MBSP)", the Funded Base Stations layer,
served as ArcGIS REST at spatial.infrastructure.gov.au. CC BY 4.0.

WHAT THIS IS, AND IS NOT. Each record is a mobile base station that Commonwealth money
(with state/carrier co-contribution) built or upgraded under MBSP Rounds 1-7, 2015-2024.
It is *where coverage was poor enough to fund a fix* — a historical remediation signal,
not a live coverage map. The nominated-black-spot database that would give current gaps
was withdrawn from data.gov.au (access now requires a login); the Queensland state
dataset was retired ("no longer publishing... available at a national level"). Funded
base stations are the best open proxy left.

Each site carries its Grantee (the carrier), so per-carrier counts are available —
Telstra took 191 of Queensland's 247 funded sites, Optus 42, FSG 9, TPG 5.

Output: data/qld_lga_mobile_blackspots.csv, one row per QLD LGA that has at least one
funded site. build_master.py left-joins it, so LGAs with none simply get 0 there.

Raw pull cached to cache/mbsp_qld_funded_base_stations.json.
"""
from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent if ROOT.name == "code" else ROOT
DATA, CACHE = BASE / "data", BASE / "cache"
for _d in (DATA, CACHE):
    _d.mkdir(exist_ok=True)

SERVICE = ("https://spatial.infrastructure.gov.au/server/rest/services/"
           "Mobile_Black_Spot_Program_Funded_Base_Stations/MapServer")
CLIENT = httpx.Client(timeout=180, follow_redirects=True,
                      headers={"User-Agent": "hackathon-research/0.1 (non-commercial)"})

# Round -> layer id, from the MapServer's own layer list.
ROUND_LAYERS = {1: 0, 2: 2, 3: 1, 4: 4, 5: 5, "5A": 6, 6: 8, 7: 12}

# Grantee strings grouped to a carrier bucket. FSG / OneWiFi are infrastructure providers,
# not retail carriers, so they land in "other".
CARRIER = {
    "telstra": "telstra",
    "optus": "optus",
    "tpg telecom": "tpg", "tpg": "tpg", "vodafone": "tpg",
}

# Same name reduction build_master.py uses, so short_name lines up on join.
TYPE_WORDS = {"council", "regional", "region", "shire", "city", "town", "authority",
              "aboriginal", "island", "area", "qld", "c", "s", "r", "ac"}

# One Round 1 site at Tweed Heads is tagged State='QLD' but sits in Tweed Shire, NSW.
NOT_QLD = {"tweed"}


def norm(name: str) -> str:
    words = re.split(r"[^a-z]+", (name or "").lower())
    return "".join(w for w in words if w and w not in TYPE_WORDS)


def carrier_of(grantee: str) -> str:
    return CARRIER.get((grantee or "").strip().lower(), "other")


def completion_year(raw: str) -> int | None:
    m = re.search(r"(19|20)\d{2}", raw or "")
    return int(m.group(0)) if m else None


def fetch_qld_sites() -> list[dict]:
    """Every QLD funded base station across all rounds, de-duplicated on MBSP_ID."""
    cache_f = CACHE / "mbsp_qld_funded_base_stations.json"
    if cache_f.exists():
        return json.loads(cache_f.read_text(encoding="utf8"))

    fields = ("MBSP_ID,Location,Grantee,State,Local_Government_Area,"
              "Remoteness,Site_Status,Completion_Date")
    seen: dict[str, dict] = {}
    for rnd, layer in ROUND_LAYERS.items():
        offset = 0
        while True:
            r = CLIENT.get(f"{SERVICE}/{layer}/query", params={
                "where": "State='QLD'", "outFields": fields, "returnGeometry": "false",
                "resultOffset": offset, "resultRecordCount": 1000, "f": "json"})
            r.raise_for_status()
            feats = r.json().get("features", [])
            for f in feats:
                a = f["attributes"]
                a["_round"] = rnd
                seen.setdefault(a.get("MBSP_ID") or f"row-{layer}-{offset}-{len(seen)}", a)
            if len(feats) < 1000:
                break
            offset += 1000
        print(f"  round {rnd:>2} (layer {layer:>2}): running total {len(seen)}")

    sites = list(seen.values())
    cache_f.write_text(json.dumps(sites, indent=1), encoding="utf8")
    print(f"  cached {len(sites)} sites -> {cache_f.name}")
    return sites


def main() -> None:
    sites = fetch_qld_sites()

    agg: dict[str, dict] = defaultdict(lambda: {
        "raw_names": set(), "total": 0, "telstra": 0, "optus": 0, "tpg": 0, "other": 0,
        "rounds": set(), "years": set()})
    dropped = []
    for s in sites:
        lga_raw = s.get("Local_Government_Area") or ""
        key = norm(lga_raw)
        if not key or key in NOT_QLD:
            dropped.append(f"{s.get('MBSP_ID')} ({lga_raw or 'no LGA'})")
            continue
        d = agg[key]
        d["raw_names"].add(lga_raw)
        d["total"] += 1
        d[carrier_of(s.get("Grantee"))] += 1
        d["rounds"].add(str(s.get("_round")))
        y = completion_year(s.get("Completion_Date"))
        if y:
            d["years"].add(y)

    rows = []
    for key, d in sorted(agg.items()):
        rows.append({
            "join_key": key,
            "mbsp_lga_raw": " / ".join(sorted(d["raw_names"])),
            "mbsp_funded_stations_total": d["total"],
            "mbsp_funded_stations_telstra": d["telstra"],
            "mbsp_funded_stations_optus": d["optus"],
            "mbsp_funded_stations_other": d["tpg"] + d["other"],
            "mbsp_rounds_covered": len(d["rounds"]),
            "mbsp_earliest_year": min(d["years"]) if d["years"] else "",
            "mbsp_latest_year": max(d["years"]) if d["years"] else "",
        })

    path = DATA / "qld_lga_mobile_blackspots.csv"
    with open(path, "w", newline="", encoding="utf8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    total = sum(r["mbsp_funded_stations_total"] for r in rows)
    tel = sum(r["mbsp_funded_stations_telstra"] for r in rows)
    print(f"\nWrote {path}")
    print(f"  {len(rows)} LGAs with >=1 funded site | {total} sites | Telstra {tel} "
          f"({100 * tel // total}%)")
    if dropped:
        print(f"  {len(dropped)} sites had no usable LGA name and were dropped: {dropped}")
    print("\nATTRIBUTION")
    print("  Mobile Black Spot Program funded base stations: Department of Infrastructure,")
    print("  Transport, Regional Development, Communications, Sport and the Arts. CC BY 4.0.")
    print("  Funded remediation 2015-2024, NOT a current coverage map — see module docstring.")


if __name__ == "__main__":
    main()
