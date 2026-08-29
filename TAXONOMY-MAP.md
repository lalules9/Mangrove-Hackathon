# Which variable answers to which risk category

Every index input mapped to the two reference taxonomies, plus what has no variable at all.
**The empty rows are the finding** — they show where the index is silent.

- **Bengio** — International AI Safety Report 2026: *malicious use · malfunctions · systemic risks*
- **Hendrycks** — An Overview of Catastrophic AI Risks (arXiv:2306.12001): *malicious use · AI race · organisational risk · rogue AI*
- **Kasirzadeh** — decisive vs accumulative (arXiv:2401.07836). Almost everything at council scale
  is **accumulative**: many small systems, one shared vendor, no single decisive event. Say this
  out loud — it is the honest reason council AI risk looks unremarkable one council at a time.

## Mapped

| Variable | Bengio | Hendrycks | Term | Note |
|---|---|---|---|---|
| `isolated_power_network` | Malicious use (cyber) · Malfunctions | Malicious use · Organisational | Exposure | 18 LGAs off the national grid. Verified from Ergon |
| `is_water_service_provider` | Malicious use (cyber) · Malfunctions | Malicious use · Organisational | Exposure | Council *is* the utility |
| `above_soci_water_threshold` | — | Organisational | Regulatory gap | Below the line = no CIRMP owed. Not a hazard, an absence of oversight |
| `has_lifeline_airstrip` | Malfunctions | Organisational | Consequence | 14 LGAs where the airstrip is the only way out |
| `road_km_total` | Malicious use (cyber) | Malicious use | Exposure | Proxy only. Traffic-control ownership unknown |
| `mean_remoteness_score` | *cross-cutting* | *cross-cutting* | Consequence | Multiplier, not a hazard |
| `seifa_irsd_score` | *cross-cutting* | *cross-cutting* | Consequence | Who absorbs a shock badly |
| `avg_persons_per_bedroom` | Malicious use (bio) | Malicious use | Consequence | Transmission multiplier |
| `indigenous_share_pct` | *cross-cutting* | *cross-cutting* | Consequence | Compounding disadvantage |
| `own_source_revenue_share` | Malfunctions | **Organisational risk** | Absorptive | No discretionary money = no response capacity |
| `indoor_staff_share` | Malfunctions | **Organisational risk** | Absorptive | Digitisation proxy; inverts vs natural hazard |
| `staff_per_1000_residents` | Malfunctions | **Organisational risk** | Absorptive | Thin staffing = no manual fallback |
| `ai_deployment_confirmed` | All three | **AI race** · Organisational | Exposure | Adoption pressure. Press-derived, 8 of 77 |

## Not mapped — nothing in the index answers these

| Category | Why it is missing | Could we get it? |
|---|---|---|
| **Bengio: malicious use — manipulation, deepfakes** | Synthetic warnings during a live emergency. No exposure data: disaster activations dataset is dead, digital inclusion is not published at LGA | Partly — Mobile Black Spot data would give a coverage proxy |
| **Bengio: systemic — labour disruption** | Occupation by LGA never pulled | Yes — one ABS Census request |
| **Bengio: systemic — vendor concentration** | LB308 is uniform across all 78, so it has no variance to score | No, not as a variable. It is a narrative finding and a recommendation |
| **Hendrycks: rogue AI / loss of control** | Not measurable at LGA level, and pretending otherwise would be dishonest | No. State that it is out of scope rather than inventing a proxy |
| **Hendrycks: AI race** | Only glanced at, via the deployment flag | Procurement registers would evidence adoption pressure properly |

## What this tells you

**Two of Bengio's three categories are represented; one is not.** Malicious use and malfunctions
are covered; systemic risk is almost entirely absent.

**Three of Hendrycks' four.** Organisational risk is the best-covered — which is unsurprising,
since institutional capacity is also the only block with no ADRI overlap. Rogue AI is absent and
should stay absent.

**The consequence terms carry most of the weight.** SEIFA, crowding, remoteness and Indigenous
share are cross-cutting vulnerability, not hazard-specific. That is legitimate — it is how ADRI
works too — but it means the index is currently better at *who suffers* than at *what happens*.

---

# Why this only covered 10 variables

The master file has **93 columns**. The table above mapped only the 10 currently wired into
`config/index.yaml`. Here is the whole file, by role:

| Role | Count | What it is |
|---|--:|---|
| **In the index** | 10 | Scored. Mapped above |
| **Held out** | 12 | Every `adri_*` column plus `median_family_income_weekly`. The control |
| **Identity** | 13 | Names, codes, website, stratum, flags |
| **Vintage / provenance** | 9 | `*_data_year`, `*_confidence`, `*_source` — metadata, never scored |
| **Narrative** | 6 | `ai_detail`, `ai_status` text, `water_utility` — evidence for the write-up, not numbers |
| **Available but unused** | **43** | The expansion candidates |

Most of those 43 are **redundant forms** of something already scored — SEIFA ships eight
variants and the index uses one; water connections appear in five columns; staff FTE in three.
Stripping the duplicates, these are the genuinely distinct signals **sitting unused**:

## Unused, and arguably should not be

| Variable | Coverage | Bengio | Hendrycks | Why it matters |
|---|--:|---|---|---|
| **`isolated_power_network`** | **78/78 verified** | Malicious use (cyber) · Malfunctions | Malicious use · Organisational | **The clearest omission.** 18 LGAs on stand-alone Ergon micro-grids with no national-grid fallback. Named on Ergon's own site. This is H1 electricity and it is not in the formula |
| `has_lifeline_airstrip` | 49/78 | Malfunctions | Organisational | 14 LGAs where the airstrip is the only way out. Pure consequence multiplier |
| `airport_control_tier` | 49/78 | Malicious use | Organisational | Council-operated vs corporatised — the same control-tier logic as water |
| `water_control_tier` | 26/78 | Malicious use | Organisational | Council-operated vs bulk-authority dependent. Sharper than the binary now used, but only a third coverage |
| `worst_remoteness_score` | 78/78 | *cross-cutting* | *cross-cutting* | Catches one isolated community inside a large LGA, which the area-weighted mean hides |
| `road_km_total` | 77/78 | Malicious use (cyber) | Malicious use | The only traffic-exposure proxy available, and traffic control is where the confirmed AI deployments actually are |
| `waste_tonnes_domestic` / `waste_properties_serviced` | 64–70/78 | Malfunctions | Organisational | Waste is a live AI deployment surface — in-truck contamination detection, pothole flagging |
| `median_age` | 78/78 | Malicious use (bio) | Malicious use | Bio-event consequence term |
| `total_operating_income_k` | 76/78 | Malfunctions | Organisational | Absolute capacity, where `own_source_revenue_share` only gives the ratio |

## What that changes

**Adding `isolated_power_network` alone would close the biggest hole in the essential-services
component.** It is verified, complete, and maps to the same category as water — yet the index
scores water and ignores power.

The others are judgement calls. `has_lifeline_airstrip` and `road_km_total` are the next most
defensible; `water_control_tier` is the sharpest measure but too thin at 26/78 to weight heavily.

**Nothing here is a redundant column problem.** It is a scope problem: the index was built from
what existed when the YAML was written, and three data pulls have landed since.
