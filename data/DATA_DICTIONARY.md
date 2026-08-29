# Data dictionary

Every column in every file in `data/`, what it means, where it came from, and how current it is.

**Currency at a glance**

| Source | Vintage | Trust |
|---|---|---|
| ADRI | analysis year **2024** | Current |
| ABS population (ERP) | **2025** | Current |
| ABS SEIFA | **2021** Census | Current release |
| ABS Census medians / Indigenous | **2021** | Current release |
| QLD staff and finance | **2015–16** | **A decade old — see the warning below** |

> **The Queensland staleness trap.** Every resource in the Queensland local government
> comparative information *open data* release stops at 2015–16, even though the portal shows a
> 2025 "last updated" date. The package metadata was touched; the data inside it was not.
> Current-year figures exist only as documents on the Department's own site, which blocks
> automated fetching — download those by hand if you need them. Every affected column here
> carries its own `*_data_year` field so the vintage travels with the number.

---

## Which file do I use? — the pipeline

**One row per LGA, 78 of them (77 councils + Weipa Town Authority), joined on `short_name`
throughout.** There is exactly one analysis table. Everything else is a step on the way to it.

```
fetch_lga_profile.py   ->  lga_profile_QLD.csv        ABS population + area + Census + SEIFA + QLD finance
fetch_adri.py          ->  adri_lga_QLD.csv           all 8 ADRI resilience themes
fetch_mbsp.py          ->  qld_lga_mobile_blackspots.csv   MBSP funded base stations per LGA, by carrier
classify_remoteness.py ->  qld_lga_remoteness.csv     official ABS Remoteness Area per LGA
(hand-curated)         ->  qld_lga_ai_inputs.csv      AI-in-infrastructure status, water utility tier
(hand-curated)         ->  qld_lga_airports.csv, qld_lga_infrastructure.csv   airstrips, roads, waste, isolated power
                              |
                              v
build_master.py       ->  qld_lga_master.csv    <-- THE analysis table. 110+ columns. Read this one.
                              |
                              v
build_index.py        ->  qld_lga_index.csv     the scored index + rank vs ADRI
                          docs/map/qld_lga_index.csv   identical copy the QAIRI map fetches (written by build_index.py)
```

The scored index is **QAIRI — the Queensland Artificial Intelligence Risk Index**. `config/index.yaml`
is its formula; `docs/map/` is its interactive form.

- **Use `qld_lga_master.csv` for any analysis.** It is what `build_index.py` reads and what the
  map is built from. If a column exists anywhere in `data/`, it is in here too.
- **`lga_profile_QLD.csv` is a build intermediate**, not a working file — it is only the ABS /
  Census / QLD-finance slice, before ADRI's other four themes, the AI layer, infrastructure and
  the black-spot data are joined on. Don't analyse from it; it will be missing columns.
- **`qld_lga_ai_inputs.csv`** (was `qld_lga_ai_risk_master.csv` — renamed to stop it reading as a
  second "master") is one hand-curated *source*: AI-in-infrastructure status per council, water
  utility control tier, published-AI-policy flag. `build_master.py` joins it in.
- Re-run order after changing any source: `fetch_*` for the source you touched, then
  `build_master.py`, then `build_index.py`.

Everything below documents columns by the file they originate in. Their final home is
`qld_lga_master.csv`.

---

## 0. `qld_lga_ai_inputs.csv` — hand-curated AI + water-control source

One row per LGA, keyed on `short_name`. A *feeder* for `build_master.py`, not the index spine.

| Column | Source | Meaning |
|---|---|---|
| `short_name`, `council_name`, `stratum`, `is_indigenous_council` | `lga_profile_QLD.csv` | Identity, carried for convenience |
| `population_latest`, `own_source_revenue_share`, `staff_fte_total` | `lga_profile_QLD.csv` | Capacity, carried for convenience |
| `adri_andri`, `adri_coping_capacity`, `adri_adaptive_capacity`, `adri_information_access` | `lga_profile_QLD.csv` | Existing disaster-resilience baseline, carried for convenience |
| `ai_status`, `ai_infrastructure_type`, `ai_source` | `research/qld_lga_ai_infrastructure_tracker.csv` | **Realized exposure** — is AI actually running in this council's infrastructure, verified against a named source |
| `water_utility`, `water_control_tier`, `water_connections_2023_24`, `meets_soci_threshold` | `water_sewer_connections_NPR_2023_24_QLD.csv` | **Current critical-infrastructure exposure** — who runs the water/sewer asset (the council, or a joint bulk authority it doesn't control alone) and whether it crosses the SOCI Act's 100,000-connection line |
| `has_published_ai_governance_policy` | derived from the policy scan (see below) | **Governance readiness** — `True` for the 3 councils with an *adopted* AI policy (Cairns, Longreach, Burdekin), `False` for the other 75. A draft (Central Highlands) counts as `False` here |
| `ai_policy_scan_result` | `research/qld_council_ai_policies.csv` | `YES` (adopted) · `DRAFT` · `DEPLOYS NO POLICY` (confirmed AI use, no governing policy) · `DISCLOSURE ONLY` · `MENTION ONLY` · `NOT FOUND` |
| `ai_policy_scope` / `ai_policy_status` | same | `all AI` vs `generative AI only`; `adopted` / `draft` / `presented` |

**Name crosswalk.** The AI tracker uses full names ("Sunshine Coast Regional"); the NPR water
file uses utility names, and Urban Utilities / Unitywater are joint authorities covering several
councils each. `build_master.py` resolves both onto `short_name` — stripping
"Regional"/"Shire"/"City"/"Council"/"Aboriginal", handling the "City of X" prefix, and mapping
the two bulk water authorities to their member councils.

**Gaps, not filled by this file:** 52 of 78 councils have no water-connection data (blank
`water_utility`) because they fall below the ~10,000-connection NPR reporting threshold. And
`ai_status` = "no evidence found" for 61 councils means not found in the sources searched, not
confirmed absent.

**This is a feature layer, not a score.** Per HANDOVER's rule, the composite is deferred — the
job is reporting realized-exposure, capacity and governance-readiness side by side so a council
can see which drives its own result.

## 1. `lga_profile_QLD.csv` — ABS / Census / finance base (build intermediate)

78 rows: Queensland's 77 local governments plus the Weipa Town Authority. One row per LGA.
Produced by `fetch_lga_profile.py`; consumed only by `build_master.py`. Analyse from
`qld_lga_master.csv` instead — this file is missing the ADRI, AI, infrastructure and black-spot
columns.

### Identity

| Column | Meaning |
|---|---|
| `short_name` | LGA name as ADRI publishes it. **This is the join key across all files.** |
| `council_name` | Full legal name. Mostly derived from a pattern — **not verified**, fix before display |
| `abs_lga_name` | Name as the ABS publishes it (LGA 2025 boundaries) |
| `abs_lga_code` | ABS LGA code, e.g. Brisbane = 31000. Use this to join any other ABS dataset |
| `website` | Verified council website. See `councils.csv` for how verification worked |
| `stratum` | Sampling stratum derived from remoteness: `seq_metro`, `regional_city`, `outer_regional`, `remote`, `very_remote`, `indigenous`. Indigenous councils are assigned to `indigenous` regardless of remoteness |
| `is_local_government` | `False` only for Weipa Town Authority. Exclude it from council counts |
| `is_indigenous_council` | One of Queensland's 17 Indigenous local governments |

### Population — ABS Estimated Resident Population, 2025

| Column | Meaning |
|---|---|
| `population_latest` | ERP for the most recent year available |
| `population_latest_year` | Which year that is |
| `population_10yr_prior` | ERP ten years earlier, for a growth or decline rate |
| `census2021_total_persons` | Census 2021 count. **Will differ from ERP** — ERP is an estimate adjusted for undercount, Census is a raw count. Do not mix them in one ratio |
| `census2021_indigenous_persons` | Aboriginal and/or Torres Strait Islander persons, Census 2021 |
| `indigenous_share_pct` | Derived: Indigenous ÷ total persons × 100, both Census 2021 |
| `population_growth_10yr_pct` | Derived: (`population_latest` − `population_10yr_prior`) ÷ prior × 100. Negative for the many councils losing population |

### Land area and density

| Column | Meaning |
|---|---|
| `area_sqkm` | Land area, km². **Computed from the boundary polygons in `docs/map/qld_lga.geojson`** (ABS ASGS 2021) with a spherical-area formula — no separate download. A few % below official ABS `AREASQKM` per LGA because the map geometry is web-resolution; fine as a *ranked* denominator, not for exact areas. See `code/fetch_lga_profile.py`. |
| `population_density_per_sqkm` | Derived: `population_latest` ÷ `area_sqkm`. Ranges from ~0.02 (Diamantina) to ~900 (Brisbane) |
| `road_density_km_per_sqkm` | Derived **in `build_master.py`** (needs `road_km_total` from `qld_lga_infrastructure.csv`): `road_km_total` ÷ `area_sqkm` |

### Census 2021 composition — ABS Census G01

Kept from the G01 table `fetch_lga_profile.py` already downloads (it previously used only two
rows of it). Each is a percentage with an explicit denominator so it can't be misread.

| Column | Meaning |
|---|---|
| `pct_aged_65_plus` | Persons 65+ ÷ total persons × 100 |
| `pct_aged_under_15` | Persons 0–14 ÷ total persons × 100 |
| `pct_language_not_english_home` | "Other language" ÷ (English only + Other language) × 100. Excludes not-stated. A proxy for exposure to synthetic-warning / scam messaging in the wrong channel |
| `pct_birthplace_overseas` | "Elsewhere" ÷ (Australia + Elsewhere) × 100 |
| `pct_year12_completed` | Year 12 or equivalent ÷ (all six "highest year of school completed" buckets) × 100 — i.e. of those who have finished schooling, the share who reached Year 12 |

### Socio-economic — ABS SEIFA 2021 and Census 2021

| Column | Meaning |
|---|---|
| `seifa_irsd_score` | Index of Relative Socio-economic **Disadvantage**. National mean 1000. **Lower = more disadvantaged.** The usual choice for vulnerability work |
| `seifa_irsd_decile_aus` | 1 = most disadvantaged decile nationally, 10 = least |
| `seifa_irsd_percentile_aus` | Percentile rank within Australia, 1–100 |
| `seifa_irsd_decile_state` | Decile rank within Queensland only. Use when comparing councils to each other rather than to the nation |
| `seifa_irsad_score` | Index of Relative Socio-economic **Advantage and Disadvantage** — two-ended. Not interchangeable with IRSD |
| `seifa_irsad_decile_aus` | National decile for IRSAD |
| `seifa_ier_score` | Index of **Economic Resources** — income, housing, wealth |
| `seifa_ieo_score` | Index of **Education and Occupation** — skills and qualifications |
| `median_age` | Years |
| `median_personal_income_weekly` | Dollars per week, persons 15+ |
| `median_household_income_weekly` | Dollars per week |
| `avg_household_size` | Persons per household. A crowding proxy, though not the ABS overcrowding measure |

> **A bug worth knowing about**, because it was in this file until it was caught. The ABS SEIFA
> dataflow ships several measures per area. `SCORE` is the area's score; `MINS` and `MAXS` are
> the *minimum and maximum scores of the SA1s inside it*. An earlier build read `MINS` as the
> score, which systematically understated disadvantage. If you pull SEIFA yourself, filter
> `SEIFA_MEASURE == "SCORE"`.

### Council capacity — Queensland CDC, **2015–16**

| Column | Meaning |
|---|---|
| `staff_data_year` | Financial year of the staff figures, format `2015_16` |
| `staff_fte_indoor` | Indoor staff, full-time equivalent. Administrative, planning, corporate, IT |
| `staff_fte_outdoor` | Outdoor staff FTE. Roads, waste, parks, water operations |
| `staff_fte_total` | Total FTE |
| `staff_per_1000_residents` | Derived. **Mixes 2015–16 staff with 2025 population** — a rough capacity indicator only. Recompute against 2016 ERP if the number matters |
| `finance_data_year` | Financial year of the finance figures |
| `total_operating_income_k` | Total operating income, thousands of dollars |
| `net_rates_and_utility_charges_k` | Net rates and utility charges, thousands. This is own-source revenue |
| `employee_expenses_k` | Employee expenses, thousands |
| `own_source_revenue_share` | Derived: rates ÷ total operating income. **The key capacity variable.** Near zero for Indigenous councils because DOGIT land is largely not valued and so not rateable |
| `water_sewer_data_year` | Financial year of the water and sewer connection figures |

### Resilience — carried through from ADRI 2024

| Column | Meaning |
|---|---|
| `adri_andri` | Composite resilience score, 0–1. **Higher = more resilient** |
| `adri_coping_capacity` | Ability to prepare for, absorb and recover from a shock |
| `adri_adaptive_capacity` | Ability to learn, adjust and transform afterwards |
| `adri_information_access` | One of the eight themes, isolated here because it is the theme closest to any AI hypothesis |
| `mean_remoteness_score` | 1 Metropolitan · 2 Inner regional · 3 Outer regional · 4 Remote · 5 Very remote. Area-weighted across the LGA's SA2s, so it is fractional |

---

## 2. `councils.csv` — the verified council register

Same 78 rows. Produced by `build_councils.py`.

| Column | Meaning |
|---|---|
| `short_name`, `council_name`, `website`, `stratum` | As above |
| `url_status` | How the website was confirmed. `verified` = HTTP 200 and the page looks like a council. `verified (blocks bots)` = the server answered **403** — it exists and refuses automated clients, which is true of **54 of 78** Queensland councils. `verified (hand-resolved)` = domain no convention predicts, looked up by hand |
| `mean_remoteness_score` | Area-weighted mean across the LGA's SA2s |
| `worst_remoteness_score` | The most remote SA2 in the LGA. Use this when a single isolated community inside a large LGA is what matters |
| `is_local_government` | `False` for Weipa Town Authority only |
| `is_indigenous_council` | One of the 17 |
| `icfp_eligible` | Receives Indigenous Councils Funding Program money — 16 of the 17. Torres Shire is excluded because it is a mainstream shire serving a largely Indigenous population. **This is why published counts differ between 16 and 17** |
| `deamalgamated_2014` | Noosa, Douglas, Livingstone, Mareeba. Split back out in 2014, and routinely confused with their pre-2014 parents by both datasets and language models |
| `adri_*` | As above |

---

## 3. `adri_lga_QLD.csv` and `adri_lga.csv` — the resilience index by LGA

Aggregated from SA2 by `fetch_adri.py`. National file has 500+ rows; Queensland file has 78.

| Column | Meaning |
|---|---|
| `state`, `lga_id`, `lga_name` | Identity. `lga_id` is ADRI's internal id, **not** the ABS LGA code |
| `sa2_count` | How many SA2s contributed. `1` means the LGA is a single SA2, so its score is that SA2's score |
| `mean_remoteness_score` | Area-weighted, 1–5 |
| `worst_remoteness_score` | Most remote constituent SA2 |
| `andri` | Composite. **0–1, higher = more resilient** |
| `coping_capacity` | Roll-up of the first six themes below |
| `adaptive_capacity` | Roll-up of the last two |
| *the eight themes* | See the official definitions below |

### The eight themes, as ADRI itself defines them

Quote these rather than paraphrasing — the wording is the authors', and using it keeps your
provenance clean. Full text is in `adri_theme_definitions.json`.

**Coping capacity**

- **`social_character`** — "The social and demographic characteristics of the community."
  Household and family composition, age, sex, education, employment, disability, language and
  length of residence.
- **`economic_capital`** — "The economic characteristics of the community." Contributes through
  mitigation, risk management, individual flexibility and adaptation.
- **`emergency_services`** — "The presence and resourcing of emergency services."
- **`planning_build_environment`** — "The presence of legislation, plans, structures or codes to
  protect communities and their built environment."
- **`community_capital`** — "The cohesion and connectedness of the community." Social capital,
  sense of community, participation, pro-social behaviour.
- **`information_access`** — "The potential for communities to engage with natural hazard
  information." Telecommunications and internet access. **The theme closest to any AI argument,
  and already the most extreme variable in the dataset**

**Adaptive capacity**

- **`govt_leadership`** — "The capacity within organisations to adaptively learn, review and
  adjust policies and procedures, or to transform organisational practices."
- **`community_social_engagement`** — "The capacity within communities to adaptively learn and
  transform in the face of complex change."

### Reading the scores honestly

- **Min–max normalised.** Aurukun scores `0.0000` on ANDRI. That is the **floor of the scale**,
  not an absence of resilience. Someone has to be zero. Reporting it as though it means nothing
  is there would be wrong, and given who lives there, careless.
- **67 of ADRI's 82 indicators sit in coping capacity**, far fewer in adaptive capacity, because
  national-scale adaptive indicators are hard to find. Adaptive scores are thinner evidence.
- **Aggregation is area-weighted.** `fetch_adri.py` weights each SA2 by area × the share of that
  SA2 inside the LGA, because the population fields in the API payload are null. Area weighting
  over-weights large empty SA2s. Joining ABS ERP by SA2 code and swapping the weight would be
  better and is a genuine improvement worth making.

---

## 4. `adri_sa2.csv` / `adri_sa2_QLD.csv` — source resolution

2,330 SA2s nationally, 529 in Queensland. Same theme columns, plus `sa2_code`, `sa2_name`,
`sa3_code`, `sa4_name`, `gccsa_name`, quartile bands, and `lga_names` listing every LGA the SA2
falls in. **Use these if you want to weight the aggregation yourself** rather than accept the
area weighting above.

---

## 5. Attribution — required, not optional

| Data | Attribute to | Licence |
|---|---|---|
| ADRI (`adri_*`, and the `adri_*` columns elsewhere) | **Natural Hazards Research Australia / University of New England** | **CC BY-NC 4.0 — non-commercial only** |
| Population, SEIFA, Census, and LGA boundaries used for `area_sqkm` (ASGS 2021) | **Australian Bureau of Statistics** | CC BY 4.0 |
| Staff, finance, water connections | **State of Queensland** | CC BY 4.0 |
| MBSP funded base stations (`mbsp_*`) | **Dept of Infrastructure, Transport, Regional Development, Communications, Sport and the Arts** | CC BY 4.0 |

The ADRI licence is the binding one: non-commercial use, attribution displayed. A hackathon
entry is non-commercial, but put the attribution on the page rather than in a footnote.

---

## 6. `water_sewer_connections_NPR_2023_24_QLD.csv` — current water/sewer connections

Fills the gap flagged above: the Queensland comparative-information water/sewer connection
figures in `lga_profile_QLD.csv` (`water_sewer_data_year`) are **2015–16**. This file is **current
to 2023–24**, sourced from the Bureau of Meteorology's **Urban National Performance Report
2023–24**, "Complete dataset" sheet, indicators `C4` ("Total number of connected properties:
water supply") and `C8` ("...wastewater"). Only Queensland service providers required to report
under the NPR framework (retail utilities above roughly 10,000 connections) are included — 22
entities, not all 77 LGAs. Smaller/remote councils' water and sewer connection counts are **still
only available from the stale 2015–16 release** — this file does not fill that part of the gap.

| Column | Meaning |
|---|---|
| `utility` | The reporting entity's own name — not always a council (see below) |
| `water_connections_2023_24` / `sewer_connections_2023_24` | Property connection counts, 2023–24 |
| `meets_soci_critical_water_asset_threshold` | `True` if either count is ≥100,000 — the *Security of Critical Infrastructure Act 2018* (Cth) threshold for a "critical water asset" |
| `notes` | Flags entities that are not a retail council utility at all |

**A unit-labelling bug worth knowing about, caught by cross-checking rather than trusting the
source file:** the BOM spreadsheet's own `Unit` column for indicators `C4`/`C8` says `population
000s`, which contradicts the indicator's own name ("connected **properties**"). Cross-checked
against `avg_household_size` and total population in `lga_profile_QLD.csv` (e.g. Cairns:
76,270 connections against ~179,000 population ≈ 2.35 people/property, matching the recorded
household size) — the values are connected properties as named, and the BOM `Unit` label is wrong,
not the data. Don't repeat BOM's own unit label without this caveat if citing the source directly.

**The finding that changes HANDOVER's H1 (SOCI critical-infrastructure) claim from general to
specific:** it is not simply true that "almost every Queensland council sits below the 100,000
connection threshold" — four entities cross it: **Urban Utilities** (676,983 water / 648,710
sewer) and **Unitywater** (358,160 / 318,537), plus **City of Gold Coast** (279,107 / 264,660) and
**Logan City Council** (142,488 / 126,947) on their own. Every other reporting QLD utility sits
well below. The structural point: Urban Utilities and Unitywater are **not councils** — they are
statutory bulk retail authorities jointly owned by, respectively, Brisbane + Ipswich + Lockyer
Valley + Scenic Rim + Somerset, and Moreton Bay + Sunshine Coast + Noosa. So for most of the SEQ
councils that *do* cross the SOCI threshold, the entity actually operating the critical
infrastructure — and therefore the one an AI-failure liability question would first land on — is a
joint authority the council partly owns, not the council itself. That is a materially different
governance/control relationship (dependent-on-another-body, not directly-operated) than for Gold
Coast and Logan, which run their own water utilities and cross the threshold directly.

**Attribution:** Bureau of Meteorology, *National Performance Report 2023–24: urban water
utilities*, © Commonwealth of Australia. Not covered by the ADRI CC BY-NC licence — BOM data has
its own terms, check before redistribution.

## 7. Joining to anything else

`abs_lga_code` is the key to the wider ABS universe. With it you can pull any LGA-level dataflow
from `data.api.abs.gov.au` — Census tables `C21_G01_LGA` through `C21_G62_LGA`, `ERP_LGA2025`,
`ABS_SEIFA2021_LGA`, `ABS_REGIONAL_LGA2021`. Add `?format=csvfilewithlabels` to any request and
the response carries both codes and human-readable labels, which saves fetching codelists.

Beware two boundary vintages in play: ADRI and Census are on **2021** boundaries, ERP is on
**2025**. For Queensland the differences are minor, but check before joining anything where a
boundary changed.

---

## 8. `qld_lga_mobile_blackspots.csv` — MBSP funded base stations

Produced by `code/fetch_mbsp.py` from the Department of Infrastructure's **Mobile Black Spot
Program — Funded Base Stations** ArcGIS service (`spatial.infrastructure.gov.au`). 62 QLD LGAs
that received at least one funded site; `build_master.py` left-joins it, so an LGA missing here
is a real **zero**, not missing data. Keyed on `join_key` (already-normalised `short_name`).

**What it measures — and what it does not.** Each source record is a mobile base station that
Commonwealth money (with state / carrier co-contribution) built or upgraded under MBSP Rounds
1–7, 2015–2024. It marks **where mobile coverage was poor enough to fund a fix** — a historical
remediation signal, *not* a current coverage or black-spot map. The nominated-black-spot database
that would show live gaps was withdrawn from data.gov.au (now behind a login); Queensland's own
dataset was retired. Funded base stations are the best open proxy left.

| Column | Meaning |
|---|---|
| `join_key` | Normalised `short_name` for the join |
| `mbsp_lga_raw` | The LGA string(s) as the source labels them — kept for audit |
| `mbsp_funded_stations_total` | Count of funded sites in the LGA, all carriers, Rounds 1–7 |
| `mbsp_funded_stations_telstra` | Of which Telstra is the grantee. **Telstra took 190 of Queensland's 246 funded sites (77%)** |
| `mbsp_funded_stations_optus` | Of which Optus |
| `mbsp_funded_stations_other` | TPG/Vodafone + infrastructure providers (Field Solutions Group, OneWiFi) |
| `mbsp_rounds_covered` | How many distinct funding rounds touched this LGA — a spread-over-time signal |
| `mbsp_earliest_year`, `mbsp_latest_year` | Completion-year range, parsed from the source's `Completion_Date` |

Derived in `build_master.py`: **`mbsp_stations_per_1000_residents`** = `mbsp_funded_stations_total`
÷ `population_latest` × 1000 — normalises the count so a remote LGA with three towers and 800
people is not swamped by a metro LGA with ten towers and 200,000.

**Attribution:** Department of Infrastructure, Transport, Regional Development, Communications,
Sport and the Arts — *Mobile Black Spot Program*. CC BY 4.0. Not covered by the ADRI CC BY-NC
licence.

---

## 9. `qld_lga_remoteness.csv` — official remoteness, as its own axis

Produced by `code/classify_remoteness.py`. `build_master.py` joins it in; the QAIRI map shows
`remoteness_category` and Indigenous status as two separate lines.

**Why it exists.** `stratum` (in `councils.csv`) is the *sampling* stratum — it buckets each LGA
by the **area-weighted** mean of its SA2 remoteness scores, and folds all 17 Indigenous councils
into one `indigenous` value. Area-weighting over-remotes large LGAs whose people all live in one
town, and the `indigenous` value hides remoteness entirely (Cherbourg and Aurukun are both just
"indigenous"). This file fixes both: it is the ABS **Remoteness Area**, and Indigenous status
stays in its own column.

**Method.** ADRI already carries the official RA of every SA2 (`adri_sa2_QLD.csv`, `remoteness`,
from the ASGS Remoteness Structure). Each LGA takes the **modal RA of its SA2s** — the category
most of its SA2s sit in, which is where the population is. Ties break to the less-remote side.
The SA2 mix is written out so every call is checkable.

| Column | Meaning |
|---|---|
| `remoteness_category` | Major City / Inner Regional / Outer Regional / Remote / Very Remote |
| `remoteness_rank` | 1 (Major City) … 5 (Very Remote) |
| `is_indigenous_council` | Carried through — an **orthogonal** axis, not a remoteness value |
| `remoteness_method` | `modal`, `modal-tie-break`, or `mean-fallback` |
| `remoteness_sa2_mix` | e.g. `Outer Regionalx2; Remotex1` — the evidence for the call |
| `differs_from_stratum` | `True` for the 8 LGAs where this disagrees with the sampling stratum |

**The 8 that move:** Redland (→ Major City — it's Greater Brisbane), Central Highlands, Charters
Towers, Maranoa, Mareeba (→ Outer Regional — the town, not the hinterland), Livingstone, Mackay,
North Burnett (→ Inner Regional). `stratum` is left as-is for the sampling design; use
`remoteness_category` for classification.

**Attribution:** ASGS Remoteness Structure, via the ADRI SA2 data — Australian Bureau of
Statistics / Natural Hazards Research Australia.
