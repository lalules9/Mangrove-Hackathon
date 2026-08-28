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

## 1. `lga_profile_QLD.csv` — the main working file

78 rows: Queensland's 77 local governments plus the Weipa Town Authority. One row per LGA.

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
| Population, SEIFA, Census | **Australian Bureau of Statistics** | CC BY 4.0 |
| Staff, finance, water connections | **State of Queensland** | CC BY 4.0 |

The ADRI licence is the binding one: non-commercial use, attribution displayed. A hackathon
entry is non-commercial, but put the attribution on the page rather than in a footnote.

---

## 6. Joining to anything else

`abs_lga_code` is the key to the wider ABS universe. With it you can pull any LGA-level dataflow
from `data.api.abs.gov.au` — Census tables `C21_G01_LGA` through `C21_G62_LGA`, `ERP_LGA2025`,
`ABS_SEIFA2021_LGA`, `ABS_REGIONAL_LGA2021`. Add `?format=csvfilewithlabels` to any request and
the response carries both codes and human-readable labels, which saves fetching codelists.

Beware two boundary vintages in play: ADRI and Census are on **2021** boundaries, ERP is on
**2025**. For Queensland the differences are minor, but check before joining anything where a
boundary changed.
