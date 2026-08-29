"""
Build the single master file: one row per Queensland LGA, every column we hold.

    python build_master.py

Sources, all joined on a normalised LGA name:
  data/lga_profile_QLD.csv        base — ABS population, area, SEIFA, Census, council finances
  data/adri_lga_QLD.csv           all eight ADRI themes (the profile carries only four)
  data/councils.csv               url_status, worst remoteness, ICFP, de-amalgamation
  data/qld_lga_ai_inputs.csv     water utility tier and 2023-24 connections, AI status
  data/qld_lga_airports.csv       lifeline airstrips, airport control tier
  data/qld_lga_infrastructure.csv roads, waste, isolated power networks
  data/qld_lga_mobile_blackspots.csv  MBSP funded base stations per LGA, by carrier
  data/qld_lga_remoteness.csv    official ABS Remoteness Area per LGA (vs the sampling stratum)
  research/disaster_events_by_lga.csv   recorded disaster events per LGA (AIDR)
  research/qld_lga_ai_infrastructure_tracker.csv   AI deployment detail and sources
  research/qld_council_ai_policies.csv             published AI policy scan (partial)

Output: data/qld_lga_master.csv

Derived here: indoor_staff_share, water_connections_best, ai_deployment_confirmed,
road_density_km_per_sqkm, mbsp_stations_per_1000_residents.

Nothing here is hand-edited. Re-run it after any source changes. If a column appears in two
sources the base wins, except where a source is explicitly newer — water connections are taken
from the 2023-24 figures where present and fall back to 2015-16.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent if ROOT.name == "code" else ROOT
DATA, RESEARCH = BASE / "data", BASE / "research"

# Entity-type words to drop. Removed on WORD boundaries, not as substrings — a substring
# replace turns "Regional" into "al" once "region" has been taken out of it, which silently
# broke 42 of 78 joins. Sources name the same council "Barcaldine", "Barcaldine Regional"
# and "Barcaldine Regional Council" interchangeably.
TYPE_WORDS = {"council", "regional", "region", "shire", "city", "town", "authority",
              "aboriginal", "island", "area", "qld", "c", "s", "r", "ac"}


def norm(name: str) -> str:
    words = re.split(r"[^a-z]+", (name or "").lower())
    return "".join(w for w in words if w and w not in TYPE_WORDS)


def load(path: Path, key: str) -> dict[str, dict]:
    if not path.exists():
        print(f"  MISSING {path.name} — skipped")
        return {}
    with open(path, encoding="utf8") as f:
        rows = list(csv.DictReader(f))
    out = {norm(r.get(key, "")): r for r in rows if r.get(key)}
    print(f"  {path.name:46} {len(rows):>3} rows -> {len(out)} keyed")
    return out


def num(v):
    try:
        return float(str(v).replace(",", "").replace("$", ""))
    except (TypeError, ValueError):
        return None


def main() -> None:
    print("Loading sources:")
    profile = load(DATA / "lga_profile_QLD.csv", "short_name")
    adri = load(DATA / "adri_lga_QLD.csv", "lga_name")
    councils = load(DATA / "councils.csv", "short_name")
    aimaster = load(DATA / "qld_lga_ai_inputs.csv", "short_name")
    tracker = load(RESEARCH / "qld_lga_ai_infrastructure_tracker.csv", "LGA")
    policies = load(RESEARCH / "qld_council_ai_policies.csv", "short_name")
    airports = load(DATA / "qld_lga_airports.csv", "short_name")
    infra    = load(DATA / "qld_lga_infrastructure.csv", "short_name")
    mbsp     = load(DATA / "qld_lga_mobile_blackspots.csv", "join_key")
    remote   = load(DATA / "qld_lga_remoteness.csv", "short_name")
    devents  = load(RESEARCH / "disaster_events_by_lga.csv", "lga_name")

    if not profile:
        raise SystemExit("lga_profile_QLD.csv is required. Run fetch_lga_profile.py first.")

    # columns to take from each secondary source (base wins on conflict)
    ADRI_THEMES = ["social_character", "economic_capital", "planning_build_environment",
                   "emergency_services", "information_access", "govt_leadership",
                   "community_social_engagement", "community_capital"]
    COUNCIL_EXTRA = ["url_status", "worst_remoteness_score", "icfp_eligible",
                     "deamalgamated_2014"]
    AI_EXTRA = ["ai_status", "ai_infrastructure_type", "ai_source", "water_utility",
                "water_control_tier", "water_connections_2023_24", "meets_soci_threshold",
                "has_published_ai_governance_policy"]

    out, misses = [], {"adri": [], "ai": [], "tracker": []}
    for k, base in profile.items():
        row = dict(base)

        a = adri.get(k, {})
        if not a:
            misses["adri"].append(base["short_name"])
        for c in ADRI_THEMES:
            row[f"adri_{c}"] = a.get(c, "")

        for c in COUNCIL_EXTRA:
            row[c] = councils.get(k, {}).get(c, "")

        m = aimaster.get(k, {})
        if not m:
            misses["ai"].append(base["short_name"])
        for c in AI_EXTRA:
            row[c] = m.get(c, "")

        t = tracker.get(k, {})
        if not t:
            misses["tracker"].append(base["short_name"])
        row["ai_detail"] = t.get("Detail", "")
        row["ai_region"] = t.get("Region", "")

        p = policies.get(k, {})
        checked = bool(p)
        row["ai_policy_scan_result"] = p.get("ai_policy_found", "not checked")
        row["ai_policy_url"] = p.get("url", "")
        # Only 27 of 78 councils were scanned. Asserting False for the other 51 would be a
        # false negative dressed as data, so unchecked councils are left blank.
        if not checked:
            row["has_published_ai_governance_policy"] = ""

        ap = airports.get(k, {})
        for c in ("airports_total", "airports_council_operated", "airports_external",
                  "has_lifeline_airstrip", "airport_control_tier"):
            row[c] = ap.get(c, "")

        inf = infra.get(k, {})
        for c in ("roads_data_year", "road_km_rural", "road_km_urban", "road_km_total",
                  "waste_data_year", "waste_properties_serviced", "waste_tonnes_domestic",
                  "waste_collection_cost_k", "isolated_power_network",
                  "isolated_power_confidence"):
            row[c] = inf.get(c, "")

        # Official ABS Remoteness Area, and Indigenous status kept as its own axis.
        # `stratum` stays the area-weighted sampling bucket; these are the classification.
        rm = remote.get(k, {})
        for c in ("remoteness_category", "remoteness_rank", "remoteness_method",
                  "remoteness_sa2_mix"):
            row[c] = rm.get(c, "")

        # Recorded disaster events (AIDR). Left join: an LGA absent from the file has
        # no recorded events, which is a real zero. Feeds the synthetic_warning component.
        de = devents.get(k, {})
        row["disaster_events_alltime"] = de.get("events_all_time", "0")
        row["disaster_events_last5yr"] = de.get("events_last_5yr", "0")

        # Mobile Black Spot Program funded base stations. Left join: an LGA absent from
        # the file received no MBSP funding, which is a real zero, not missing data.
        mb = mbsp.get(k, {})
        row["mbsp_lga_raw"] = mb.get("mbsp_lga_raw", "")
        for c in ("mbsp_funded_stations_total", "mbsp_funded_stations_telstra",
                  "mbsp_funded_stations_optus", "mbsp_funded_stations_other",
                  "mbsp_rounds_covered"):
            row[c] = mb.get(c, "0")
        for c in ("mbsp_earliest_year", "mbsp_latest_year"):
            row[c] = mb.get(c, "")

        # ---- derived ----------------------------------------------------------
        ind, tot = num(row.get("staff_fte_indoor")), num(row.get("staff_fte_total"))
        row["indoor_staff_share"] = round(ind / tot, 3) if ind and tot else ""

        area = num(row.get("area_sqkm"))
        roads = num(row.get("road_km_total"))
        row["road_density_km_per_sqkm"] = round(roads / area, 4) if roads and area else ""

        pop = num(row.get("population_latest"))
        mb_total = num(row.get("mbsp_funded_stations_total"))
        row["mbsp_stations_per_1000_residents"] = (
            round(1000 * mb_total / pop, 3) if mb_total is not None and pop else "")

        # water connections: prefer 2023-24, fall back to 2015-16, record which
        new, old = num(row.get("water_connections_2023_24")), num(row.get("water_connections_total"))
        if new is not None:
            row["water_connections_best"], row["water_connections_vintage"] = int(new), "2023_24"
        elif old is not None:
            row["water_connections_best"], row["water_connections_vintage"] = int(old), "2015_16"
        else:
            row["water_connections_best"] = row["water_connections_vintage"] = ""

        # Three states, not two. "Confirmed AI" -> True. "No evidence found" -> blank
        # (missing, so components_complete honestly reports it as incomplete rather than
        # scoring it as a safe zero). Everything else checked (AI-adjacent, state-deployed
        # but not council-run) -> False.
        _ai = (row.get("ai_status") or "").strip().lower()
        row["ai_deployment_confirmed"] = ("True" if _ai.startswith("confirmed")
                                          else "" if _ai in ("", "no evidence found")
                                          else "False")

        out.append(row)

    # stable column order: identity, then thematic blocks
    cols = list(out[0].keys())
    path = DATA / "qld_lga_master.csv"
    with open(path, "w", newline="", encoding="utf8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(out)

    print(f"\nWrote {path}")
    print(f"  {len(out)} rows x {len(cols)} columns")
    for label, names in misses.items():
        if names:
            print(f"  no {label} match ({len(names)}): {', '.join(names[:6])}"
                  f"{' ...' if len(names) > 6 else ''}")

    filled = lambda c: sum(1 for r in out if r.get(c) not in ("", None))
    print("\n  coverage of the joined-in columns:")
    for c in (ADRI_THEMES[:2] + ["url_status", "water_control_tier",
                                 "water_connections_best", "ai_status",
                                 "ai_deployment_confirmed", "indoor_staff_share",
                                 "area_sqkm", "population_density_per_sqkm",
                                 "road_density_km_per_sqkm",
                                 "mbsp_funded_stations_total"]):
        key = f"adri_{c}" if c in ADRI_THEMES else c
        print(f"    {key:34} {filled(key):>3}/{len(out)}")


if __name__ == "__main__":
    main()
