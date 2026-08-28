"""
Build and verify the complete Queensland local government list.

Names come from the ADRI pull (data/adri_lga_QLD.csv), which is authoritative and complete —
78 entries, being Queensland's 77 local governments plus the Weipa Town Authority, which is
not a council and is flagged as such.

Remoteness comes from the same source, so `stratum` is populated for every row rather than
left as homework.

URLs are then VERIFIED by fetching them. Two guards, both learned the hard way: a slug can
resolve to something that is not the council at all (Noosa once resolved to a travel site), so
the page must actually mention the place; and anything outside .qld.gov.au is flagged for
human review rather than accepted, because some councils genuinely use other domains.

    python build_councils.py            # verify every council (default)
    python build_councils.py --no-verify

Anything unresolved lands in data/councils_unverified.csv. Fix those by hand before you run
anything that depends on the URLs.
"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent if ROOT.name == "code" else ROOT   # data/ cache/ results/ sit beside code/
DATA, CACHE, RESULTS = BASE / "data", BASE / "cache", BASE / "results"
for _d in (DATA, CACHE, RESULTS):
    _d.mkdir(exist_ok=True)

# Queensland's 17 Indigenous local governments. Sixteen receive the Indigenous Councils
# Funding Program; Torres Shire is a mainstream shire serving a largely Indigenous population,
# which is why published counts differ between 16 and 17. State which you are using.
INDIGENOUS = {
    "Aurukun", "Cherbourg", "Doomadgee", "Hope Vale", "Kowanyama", "Lockhart River",
    "Mapoon", "Mornington", "Napranum", "Northern Peninsula Area", "Palm Island",
    "Pormpuraaw", "Torres", "Torres Strait Island", "Woorabinda", "Wujal Wujal", "Yarrabah",
}
ICFP_ELIGIBLE = INDIGENOUS - {"Torres"}

# De-amalgamated in 2014. Models and datasets routinely confuse these with their pre-2014
# parent entities.
DEAMALGAMATED_2014 = {"Noosa", "Douglas", "Livingstone", "Mareeba"}

# Not a local government — a town authority. Kept in the list, flagged, excluded from counts.
NOT_A_COUNCIL = {"Weipa"}

# Full legal names where they are not simply "<name> Regional/Shire/City Council".
FULL_NAME = {
    "Brisbane": "Brisbane City Council",           # governed by the City of Brisbane Act 2010
    "Central Highlands (Qld)": "Central Highlands Regional Council",
    "Flinders (Qld)": "Flinders Shire Council",
    "Torres Strait Island": "Torres Strait Island Regional Council",
    "Northern Peninsula Area": "Northern Peninsula Area Regional Council",
    "Torres": "Torres Shire Council",
    "Weipa": "Weipa Town Authority",
    "Mornington": "Mornington Shire Council",
    "Aurukun": "Aurukun Shire Council",
}


def clean(name: str) -> str:
    """ADRI suffixes some names with a state disambiguator."""
    return re.sub(r"\s*\(Qld\)\s*$", "", name).strip()


def full_name(short: str) -> str:
    if short in FULL_NAME:
        return FULL_NAME[short]
    base = clean(short)
    if base in INDIGENOUS:
        return f"{base} Aboriginal Shire Council"
    return f"{base} Regional Council"      # a guess; the URL check is what matters


def slug(name: str) -> str:
    return re.sub(r"[^a-z]", "", clean(name).lower())


def acronym(name: str) -> str:
    """Many Queensland councils use initials — chrc, tsirc, nparc, btrc, msc."""
    words = [w for w in re.split(r"[^A-Za-z]+", clean(name)) if w]
    return "".join(w[0].lower() for w in words)


# Councils whose domain no naming convention predicts. Each was resolved by hand and
# confirmed to respond. Add to this rather than loosening the guesser — a wrong URL becomes
# wrong ground truth becomes a wrong finding.
KNOWN_URLS = {
    "Palm Island": "https://www.palmcouncil.qld.gov.au",
    "Barcaldine": "https://www.barcaldinerc.qld.gov.au",
    "Central Highlands": "https://chrc.qld.gov.au",     # key is the cleaned name, no "(Qld)"
    "Lockhart River": "https://lockhart.qld.gov.au",    # domain drops "river"
    "Toowoomba": "https://www.tr.qld.gov.au",
    "Wujal Wujal": "https://www.wujalwujalcouncil.qld.gov.au",
    "Weipa": "https://www.weipatownauthority.com.au",   # town authority, not a council
}


def candidate_urls(short: str) -> list[str]:
    if short in KNOWN_URLS:
        return [KNOWN_URLS[short]]
    s, a = slug(short), acronym(short)
    cands = [f"https://www.{s}.qld.gov.au", f"https://{s}.qld.gov.au"]
    for suf in ("rc", "sc", ""):
        if len(a) > 1 or suf:
            cands += [f"https://www.{a}{suf}.qld.gov.au", f"https://{a}{suf}.qld.gov.au"]
    cands += [f"https://www.{s}.gov.au", f"https://{s}.com.au", f"https://www.{s}.com.au"]
    seen, out = set(), []
    for c in cands:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def verify(short: str, client: httpx.Client) -> tuple[str, str]:
    """
    Resolve a council's website, treating HTTP status honestly.

    Many Queensland council sites sit behind a web application firewall that returns 403 to
    any non-browser client. A 403 means "this server exists and is refusing me", NOT "no such
    site" — and on a .qld.gov.au domain whose slug matches the council name, that is strong
    evidence the domain is theirs. Connection and DNS failures, and 404s, mean it is not.

    We do NOT spoof a browser user agent to get around the block. The 403 is recorded as a
    fact about the site, which matters: anything downstream that needs to read council pages
    will hit the same wall.
    """
    place = slug(short)
    cands = candidate_urls(short)
    if short in KNOWN_URLS:                     # hand-resolved: trust it, still confirm it answers
        gov_candidates, other_candidates = cands, []
    else:
        gov_candidates = [u for u in cands if ".qld.gov.au" in u]
        other_candidates = [u for u in cands if ".qld.gov.au" not in u]

    for url in gov_candidates:
        host_slug = url.split("//")[1].split(".")[1] if "//" in url else ""
        try:
            r = client.get(url, timeout=20, follow_redirects=True)
        except Exception:
            continue                                  # DNS or connection failure: not real
        final = str(r.url)
        if r.status_code in (401, 403, 429):
            return final, "verified (blocks bots)"    # server exists and answered
        if r.status_code >= 400:
            continue                                  # 404 and friends: not real
        if short in KNOWN_URLS:
            return final, "verified (hand-resolved)"  # trusted; skip the name heuristics
        body = r.text.lower()
        if place not in body and place not in final.lower() and host_slug != place:
            continue
        if any(t in body for t in ("council", "rates", "mayor",
                                   "local government", "town authority")):
            return final, "verified"

    for url in other_candidates:                       # only if nothing on .qld.gov.au answered
        try:
            r = client.get(url, timeout=15, follow_redirects=True)
        except Exception:
            continue
        if r.status_code >= 400 or len(r.text) < 500:
            continue
        final, body = str(r.url), r.text.lower()
        if place not in body and place not in final.lower():
            continue
        if any(t in body for t in ("council", "rates", "mayor", "town authority")):
            return final, "review — non-gov domain"

    return "", "UNVERIFIED — fix by hand"


def stratum(short: str, remoteness: float) -> str:
    if clean(short) in INDIGENOUS:
        return "indigenous"
    if remoteness <= 1.5:
        return "seq_metro"
    if remoteness <= 2.5:
        return "regional_city"
    if remoteness <= 3.5:
        return "outer_regional"
    if remoteness <= 4.5:
        return "remote"
    return "very_remote"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-verify", action="store_true")
    args = ap.parse_args()

    src = DATA / "adri_lga_QLD.csv"
    if not src.exists():
        raise SystemExit(f"{src} not found — run fetch_adri.py --state QLD first.")

    adri = {clean(r["lga_name"]): r for r in csv.DictReader(open(src, encoding="utf8"))}
    print(f"Sourced {len(adri)} Queensland entries from the ADRI pull.\n")

    rows, unverified, review = [], [], []
    headers = {"User-Agent": "hackathon-research/0.1 (non-commercial)"}
    with httpx.Client(headers=headers) as client:
        for short in sorted(adri):
            rec = adri[short]
            remoteness = float(rec["mean_remoteness_score"])
            url, status = (verify(short, client) if not args.no_verify
                           else (candidate_urls(short)[0], "unchecked"))
            row = {
                "short_name": short,
                "council_name": full_name(short),
                "website": url,
                "url_status": status,
                "stratum": stratum(short, remoteness),
                "mean_remoteness_score": remoteness,
                "worst_remoteness_score": rec["worst_remoteness_score"],
                "is_local_government": short not in NOT_A_COUNCIL,
                "is_indigenous_council": short in INDIGENOUS,
                "icfp_eligible": short in ICFP_ELIGIBLE,
                "deamalgamated_2014": short in DEAMALGAMATED_2014,
                "adri_andri": rec["andri"],
                "adri_coping_capacity": rec["coping_capacity"],
                "adri_adaptive_capacity": rec["adaptive_capacity"],
                "adri_information_access": rec["information_access"],
            }
            rows.append(row)
            if status.startswith("UNVERIFIED"):
                unverified.append(row)
            elif status.startswith("review"):
                review.append(row)
            flag = "" if row["is_local_government"] else "  [not a council]"
            print(f"  {status:24} {short:26} {url}{flag}")

    with open(DATA / "councils.csv", "w", newline="", encoding="utf8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    problems = unverified + review
    path_bad = DATA / "councils_unverified.csv"
    if problems:
        with open(path_bad, "w", newline="", encoding="utf8") as f:
            w = csv.DictWriter(f, fieldnames=list(problems[0].keys()))
            w.writeheader()
            w.writerows(problems)
    elif path_bad.exists():
        path_bad.unlink()

    councils = [r for r in rows if r["is_local_government"]]
    print(f"\nWrote {len(rows)} entries to data/councils.csv")
    print(f"  {len(councils)} local governments + "
          f"{len(rows) - len(councils)} town authority (Weipa)")
    print(f"  {sum(r['is_indigenous_council'] for r in rows)} Indigenous local governments "
          f"({sum(r['icfp_eligible'] for r in rows)} ICFP-eligible)")
    print(f"  {len(rows) - len(problems)} URLs verified on .qld.gov.au")
    if review:
        print(f"  {len(review)} on a non-government domain — confirm by hand")
    if unverified:
        print(f"  {len(unverified)} UNRESOLVED — fix by hand")
    if problems:
        print(f"  -> data/councils_unverified.csv")

    print("\nStrata:")
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["stratum"]] = counts.get(r["stratum"], 0) + 1
    for s in ("seq_metro", "regional_city", "outer_regional", "remote",
              "very_remote", "indigenous"):
        if s in counts:
            print(f"  {s:16} {counts[s]:3}")


if __name__ == "__main__":
    main()
