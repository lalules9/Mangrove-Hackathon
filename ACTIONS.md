# Actions

Every open to-do in one place. Updated 29 Aug 2026. Delete lines as they are done.

## P1 — needed for a defensible submission

| # | Action | Why | Effort | Who |
|---|---|---|---|---|
| 1 | **Decide whether `ai_deployment_confirmed` stays in the index** | It is press-derived (8 of 77) and drives the whole divergence: Spearman −0.671 with it, −0.843 without. This is the finding a judge will attack | 20 min decision | Both |
| 2 | **Write the limitations page** before results are final | A scored criterion. Name what was checked, what wasn't, what would change the conclusion | 1 hr | Julie |
| 3 | **Pre-register the prediction** with a timestamp, then commit it | Converts a demo into an experiment. Prediction already stated: metros rank worse than ADRI, Spearman < 0.9. Both held | 15 min | Paul |
| 4 | **Fix `council_name`** — most are pattern-derived (`<name> Regional Council`) and wrong for some shires | These appear on screen in the map popup | 30 min from the Dept directory | Either |
| 5 | **Reconcile the 77 vs 78 count** — Julie's list includes Weipa Town Authority as an LGA; ours flags it `is_local_government=False`. Also her "Confirmed AI (8)" lists nine councils | Pick one convention, state it once | 15 min | Both |

## P2 — real improvements, do if time allows

| # | Action | Why | Effort |
|---|---|---|---|
| 6 | **Mobile Black Spot data** — download manually from data.gov.au (the ZIP 302s to HTML for scripts) | The only route to a telco/coverage variable. Feeds the synthetic-warning hazard, which currently has *no* exposure data | 30 min manual |
| 7 | **Occupation by LGA** from ABS Census | The only missing Bengio category we can actually close (systemic/labour). One API call | 45 min |
| 8 | **Contract registers ($200k, s 237 LG Reg 2012)** for real vendor evidence | Replaces press-derived deployment data with procurement fact. Would fix action 1 properly | ~1 day, 78 PDFs |
| 9 | **Add `traces_to` to each component in `config/index.yaml`** | Makes the taxonomy lineage visible in the formula itself, not just in TAXONOMY-MAP.md | 20 min |
| 10 | **Population-weight the ADRI SA2→LGA rollup** — currently area-weighted, which over-weights large empty SA2s | Join ABS ERP by SA2 code and swap the weight in `fetch_adri.py` | 1 hr |

## P3 — nice to have

| # | Action |
|---|---|
| 13 | Input-level sliders on the map (currently component-level only) |
| 14 | Julie's source list as an appendix or popup on the map |
| 15 | Traffic-signal ownership per LGA — council vs TMR. No dataset found; may not exist |
| 16 | `water_control_tier` is only 26/78 — extend or state the gap |

## Blocked / abandoned — with reasons

| Item | Status |
|---|---|
| **DRFA disaster activations by LGA** | **Dead.** data.qld entry is 2022 and its download URL points at a domain that no longer resolves. QRA activations page 404s. PDF only |
| **ADII digital inclusion at LGA** | **Not published at that resolution.** State/SA4 only. Use `adri_information_access` instead |
| **Travel time to ICU** | **Needs routing.** Straight-line distance is meaningless for island and Cape communities |
| **Ergon isolated communities** | **Done** — 18 LGAs verified from ergon.com.au, replacing 22 inferred |
| **AI policy scan** | **Done — all 78 councils** (`research/qld_council_ai_policies.csv`). 3 adopted (Cairns, Longreach, Burdekin), 1 draft (Central Highlands), 5 deploy AI with no policy, 2 disclosure/mention only, 67 nothing found. Councils block automated crawling, so this is web-search depth; the four policy docs were read via search, not opened directly |
| **LB308 as an index variable** | **Not usable.** Uniform across all 78, no variance. It is a narrative finding and a recommendation, not a column |
| **GitHub Pages** | **Blocked on Julie** — admin only. Settings → Pages → `main` → `/docs`. Map is published as an artifact in the meantime |

## Corrections already made — do not reintroduce

- Councils do **not** run health, schools, police, housing, welfare or transport
- Robodebt is a **failure taxonomy**, not a compliance bar — score proportionality
- Remoteness is **not** monotonic; decompose exposure / absorptive / consequence
- Do **not** propose Australian councils adopt the EU regime; borrow the questions only
- The Gemini API is **not** Google's AI Overview
- ADRI's connectivity indicators **were** refreshed — the ADSL staleness angle does not hold
- Disclosure threshold is **s 237, $200,000**; s 226's $280,000 is the tender threshold
