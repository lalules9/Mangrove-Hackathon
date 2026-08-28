"""
Assemble a standard profile for every Queensland local government area.

    python fetch_lga_profile.py            # Queensland
    python fetch_lga_profile.py --national

Pulls from two places and joins them onto the 78-row council list:

  ABS SDMX API   data.api.abs.gov.au — population, SEIFA disadvantage, Census medians,
                 Indigenous population. Current, free, no key needed.
  data.qld.gov.au  council staff numbers and finances, from the Consolidated Data Collection.

A WARNING ABOUT THE STAFF NUMBERS. Every resource in the Queensland comparative information
open-data release stops at **2015-16**, whatever the portal's "last updated" date says. The
package metadata was touched in 2025; the data inside it was not. Current-year figures exist
only as documents on the Department's own site, which blocks automated fetching — download
those by hand if you need them. Staff and finance columns here are a decade old and are
labelled with their year so you cannot forget it.

ABS data is Creative Commons Attribution 4.0 — attribute the Australian Bureau of Statistics.
Queensland open data is CC BY 4.0 — attribute the State of Queensland.
"""
from __future__ import annotations

import argparse
import csv
import io
import re
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent if ROOT.name == "code" else ROOT
DATA, CACHE = BASE / "data", BASE / "cache"
for _d in (DATA, CACHE):
    _d.mkdir(exist_ok=True)

ABS = "https://data.api.abs.gov.au/rest/data"
QLD_RES = "https://www.data.qld.gov.au/dataset/c7c0c31e-a844-480d-bfbe-4b689179a5cf/resource"

CLIENT = httpx.Client(timeout=300, follow_redirects=True,
                      headers={"User-Agent": "hackathon-research/0.1 (non-commercial)"})


def cached(name: str, url: str) -> str:
    f = CACHE / f"{name}.csv"
    if f.exists():
        return f.read_text(encoding="utf8")
    r = CLIENT.get(url)
    r.raise_for_status()
    f.write_text(r.text, encoding="utf8")
    print(f"  fetched {name}  ({len(r.text):,} bytes)")
    return r.text


def rows(text: str) -> list[dict]:
    return list(csv.DictReader(io.StringIO(text)))


# --------------------------------------------------------------------------- name matching

# Order matters: longest first. Do NOT add "island regional council" — it would strip the
# "Island" out of Torres Strait Island Regional Council and break the join.
SUFFIXES = [
    "aboriginal shire council", "regional council", "shire council",
    "city council", "town authority", "council",
    "(qld)", "(c)", "(s)", "(r)", "(ac)", "(t)", "(m)", "(dc)",
]


def norm(name: str) -> str:
    """Reduce a council or LGA name to a comparable key."""
    s = (name or "").lower().strip()
    for suf in SUFFIXES:
        s = s.replace(suf, " ")
    s = re.sub(r"[^a-z]", "", s)
    # a few genuine spelling divergences between sources
    return {"mountisa": "mountisa", "northernpeninsulaarea": "northernpeninsulaarea"}.get(s, s)


# --------------------------------------------------------------------------- ABS pulls

def abs_population() -> dict[str, dict]:
    """Estimated Resident Population by LGA — latest year and ten years prior."""
    out: dict[str, dict] = {}
    txt = cached("abs_erp_lga2025",
                 f"{ABS}/ABS,ERP_LGA2025,1.0.0/all?format=csvfilewithlabels")
    for r in rows(txt):
        if r.get("REGION_TYPE") != "LGA2025":
            continue
        k = norm(r.get("Region", ""))
        yr, val = r.get("TIME_PERIOD"), r.get("OBS_VALUE")
        if not k or not yr or not val:
            continue
        d = out.setdefault(k, {"lga_code": r.get("REGION"), "abs_name": r.get("Region")})
        d[f"erp_{yr}"] = val
    return out


def abs_seifa() -> dict[str, dict]:
    """SEIFA 2021 — IRSD (disadvantage) and IRSAD, score and decile."""
    out: dict[str, dict] = {}
    txt = cached("abs_seifa2021_lga",
                 f"{ABS}/ABS,ABS_SEIFA2021_LGA,1.0.0/all?format=csvfilewithlabels")
    keep = {"IRSD": "irsd", "IRSAD": "irsad", "IER": "ier", "IEO": "ieo"}
    # SEIFA_MEASURE codes, from the ABS codelist:
    #   SCORE = the area's score        RWAD = rank within Australia, decile
    #   RWAP  = percentile (Australia)  RWSD = rank within state, decile
    #   MINS/MAXS = min/max score of the SA1s inside the area — NOT the area score.
    #   Reading MINS as the score understates disadvantage; do not do it.
    measures = {"SCORE": "score", "RWAD": "decile_aus", "RWAP": "percentile_aus",
                "RWSD": "decile_state", "URP": "population"}
    for r in rows(txt):
        idx = r.get("SEIFAINDEXTYPE")
        meas = measures.get((r.get("SEIFA_MEASURE") or "").upper())
        if idx not in keep or not meas:
            continue
        code, val = r.get("LGA_2021"), r.get("OBS_VALUE")
        if not code or not val:
            continue
        if meas == "population":
            if idx == "IRSD":
                out.setdefault(code, {})["seifa_usual_resident_population"] = val
            continue
        out.setdefault(code, {})[f"seifa_{keep[idx]}_{meas}"] = val
    return out


def abs_census_medians() -> dict[str, dict]:
    """Census 2021 G02 — selected medians and averages by LGA."""
    out: dict[str, dict] = {}
    try:
        txt = cached("abs_c21_g02_lga",
                     f"{ABS}/ABS,C21_G02_LGA,1.0.0/all?format=csvfilewithlabels")
    except Exception as e:
        print(f"  (census medians unavailable: {e})")
        return out
    want = {"median age": "median_age",
            "median total personal income": "median_personal_income_weekly",
            "median total household income": "median_household_income_weekly",
            "average household size": "avg_household_size",
            "median mortgage repayment": "median_mortgage_monthly",
            "median rent": "median_rent_weekly"}
    for r in rows(txt):
        code = r.get("REGION")
        label = (r.get("Median/Average") or "").lower()
        val = r.get("OBS_VALUE")
        if not code or not val:
            continue
        for frag, col in want.items():
            if frag in label:
                out.setdefault(code, {})[col] = val
                break
    return out


def abs_indigenous() -> dict[str, dict]:
    """Census 2021 G01 — total persons and Aboriginal and/or Torres Strait Islander persons."""
    out: dict[str, dict] = {}
    try:
        txt = cached("abs_c21_g01_lga",
                     f"{ABS}/ABS,C21_G01_LGA,1.0.0/all?format=csvfilewithlabels")
    except Exception as e:
        print(f"  (census G01 unavailable: {e})")
        return out
    for r in rows(txt):
        if (r.get("SEXP") or "") != "3":                      # 1=Males 2=Females 3=Persons
            continue
        code = r.get("REGION")
        label = (r.get("Selected person characteristic") or "").lower()
        val = r.get("OBS_VALUE")
        if not code or not val:
            continue
        if label.strip() == "total persons":
            out.setdefault(code, {})["census_total_persons"] = val
        elif label.strip() == ("aboriginal and/or torres strait islander "
                               "persons: total"):
            out.setdefault(code, {})["census_indigenous_persons"] = val
    return out


# --------------------------------------------------------------------------- Queensland pulls

def qld_resource(name: str, path: str) -> list[dict]:
    return rows(cached(f"qld_{name}", f"{QLD_RES}/{path}"))


def qld_latest_by_council(recs: list[dict]) -> dict[str, dict]:
    """
    Keep the most recent year for each council.

    Column names differ between resources in this collection: personnel uses
    "Council Name" and "Year", financial uses "Local Government" and "Financial Year".
    Detect rather than assume.
    """
    if not recs:
        return {}
    cols = list(recs[0].keys())
    name_col = next((c for c in cols if c in ("Council Name", "Local Government")
                     or "council" in c.lower() or "local government" == c.lower()), cols[0])
    year_col = next((c for c in cols if "year" in c.lower()), None)
    best: dict[str, dict] = {}
    for r in recs:
        k = norm(r.get(name_col, ""))
        if not k:
            continue
        r["_year"] = r.get(year_col, "") if year_col else ""
        if k not in best or r["_year"] > best[k]["_year"]:
            best[k] = r
    return best


def num(v) -> str:
    return (v or "").replace(",", "").replace("$", "").strip()


# --------------------------------------------------------------------------- assemble

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--national", action="store_true")
    args = ap.parse_args()

    councils_path = DATA / "councils.csv"
    if not councils_path.exists():
        raise SystemExit("data/councils.csv not found — run build_councils.py first.")
    councils = list(csv.DictReader(open(councils_path, encoding="utf8")))
    print(f"Base list: {len(councils)} Queensland entries\n")

    print("Fetching ABS...")
    pop, seifa = abs_population(), abs_seifa()
    medians, indig = abs_census_medians(), abs_indigenous()

    print("Fetching Queensland Consolidated Data Collection...")
    staff = qld_latest_by_council(qld_resource(
        "personnel",
        "9e81cb82-d71e-4c2d-ad2b-54a053cfeadf/download/"
        "qld-local-government-comparative-information-report-cdc-personnel.csv"))
    fin = qld_latest_by_council(qld_resource(
        "financial",
        "2dd25c9b-cc5b-4c81-876f-97d277e88889/download/"
        "qld-local-government-comparative-information-report-cdc-financial-inputs.csv"))
    water = qld_latest_by_council(qld_resource(
        "water_connections",
        "3c2d90f5-e9e5-4f6e-8ca0-a96580a08a9e/download/"
        "qld-local-government-comparative-information-report-cdc-water-sewer-connections.csv"))

    erp_years = sorted({k for d in pop.values() for k in d if k.startswith("erp_")})
    latest_erp = erp_years[-1] if erp_years else None
    older_erp = erp_years[-11] if len(erp_years) > 11 else (erp_years[0] if erp_years else None)

    out, misses = [], {"abs": [], "staff": [], "fin": []}
    for c in councils:
        k = norm(c["short_name"])
        p = pop.get(k, {})
        code = p.get("lga_code", "")
        s = seifa.get(code, {})
        m = medians.get(code, {})
        i = indig.get(code, {})
        st = staff.get(k, {})
        fi = fin.get(k, {})
        wa = water.get(k, {})

        if not p:
            misses["abs"].append(c["short_name"])
        if not st:
            misses["staff"].append(c["short_name"])
        if not fi:
            misses["fin"].append(c["short_name"])

        row = {
            "short_name": c["short_name"],
            "council_name": c["council_name"],
            "abs_lga_name": p.get("abs_name", ""),
            "abs_lga_code": code,
            "stratum": c["stratum"],
            "is_local_government": c["is_local_government"],
            "is_indigenous_council": c["is_indigenous_council"],
            "website": c["website"],
            # --- population
            "population_latest": p.get(latest_erp, "") if latest_erp else "",
            "population_latest_year": (latest_erp or "").replace("erp_", ""),
            "population_10yr_prior": p.get(older_erp, "") if older_erp else "",
            "census2021_total_persons": i.get("census_total_persons", ""),
            "census2021_indigenous_persons": i.get("census_indigenous_persons", ""),
            # --- socio-economic
            "seifa_irsd_score": s.get("seifa_irsd_score", ""),
            "seifa_irsd_decile_aus": s.get("seifa_irsd_decile_aus", ""),
            "seifa_irsd_percentile_aus": s.get("seifa_irsd_percentile_aus", ""),
            "seifa_irsd_decile_state": s.get("seifa_irsd_decile_state", ""),
            "seifa_irsad_score": s.get("seifa_irsad_score", ""),
            "seifa_irsad_decile_aus": s.get("seifa_irsad_decile_aus", ""),
            "seifa_ier_score": s.get("seifa_ier_score", ""),
            "seifa_ieo_score": s.get("seifa_ieo_score", ""),
            "median_age": m.get("median_age", ""),
            "median_personal_income_weekly": m.get("median_personal_income_weekly", ""),
            "median_household_income_weekly": m.get("median_household_income_weekly", ""),
            "avg_household_size": m.get("avg_household_size", ""),
            # --- council capacity (STALE — see module docstring)
            "staff_data_year": st.get("Year", ""),
            "staff_fte_indoor": num(st.get("Number of INDOOR staff (FTE) employed by council")),
            "staff_fte_outdoor": num(st.get("Number of OUTDOOR staff (FTE) employed by council")),
            "staff_fte_total": num(st.get("Total Number of staff (FTE) employed by council")),
            "finance_data_year": fi.get("_year", ""),
            "total_operating_income_k": num(fi.get("Total operating Income - $'000")),
            "net_rates_and_utility_charges_k": num(
                fi.get("Net rates and utility charges - $'000")),
            "employee_expenses_k": num(fi.get("Employee expenses - $'000")),
            "water_sewer_data_year": wa.get("_year", ""),
            # --- ADRI, carried through
            "adri_andri": c.get("adri_andri", ""),
            "adri_coping_capacity": c.get("adri_coping_capacity", ""),
            "adri_adaptive_capacity": c.get("adri_adaptive_capacity", ""),
            "adri_information_access": c.get("adri_information_access", ""),
            "mean_remoteness_score": c.get("mean_remoteness_score", ""),
        }
        # derived
        try:
            tot = float(row["census2021_total_persons"]); ind = float(row["census2021_indigenous_persons"])
            row["indigenous_share_pct"] = round(100 * ind / tot, 1) if tot else ""
        except (ValueError, TypeError):
            row["indigenous_share_pct"] = ""
        try:
            inc = float(row["total_operating_income_k"])
            rates = float(row["net_rates_and_utility_charges_k"])
            row["own_source_revenue_share"] = round(rates / inc, 3) if inc else ""
        except (ValueError, TypeError, ZeroDivisionError):
            row["own_source_revenue_share"] = ""
        try:
            row["staff_per_1000_residents"] = round(
                1000 * float(row["staff_fte_total"]) / float(row["population_latest"]), 2)
        except (ValueError, TypeError, ZeroDivisionError):
            row["staff_per_1000_residents"] = ""
        out.append(row)

    path = DATA / "lga_profile_QLD.csv"
    with open(path, "w", newline="", encoding="utf8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)

    filled = lambda col: sum(1 for r in out if r[col])
    print(f"\nWrote {path}  ({len(out)} rows, {len(out[0])} columns)\n")
    print("Coverage:")
    for col in ("population_latest", "seifa_irsd_score", "seifa_irsd_decile_aus",
                "seifa_ier_score", "median_age",
                "census2021_indigenous_persons", "indigenous_share_pct",
                "staff_fte_total", "total_operating_income_k",
                "own_source_revenue_share"):
        print(f"  {col:32} {filled(col):3}/{len(out)}")
    for label, names in misses.items():
        if names:
            print(f"\n  no {label} match ({len(names)}): {', '.join(names[:8])}"
                  f"{' ...' if len(names) > 8 else ''}")

    print("\nATTRIBUTION")
    print("  Population, SEIFA and Census: Australian Bureau of Statistics, CC BY 4.0.")
    print("  Staff and finance: State of Queensland, CC BY 4.0. DATA IS 2015-16 — see docstring.")


if __name__ == "__main__":
    main()
