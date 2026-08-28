# HANDOVER — Mangrove Ground-level Governance Hackathon

**Written:** 29 August 2026
**For:** Julie and Paul, to pick this up without access to the Claude Code session it came from.
**Read this first.** Everything else in this folder is referenced from here.

---

## 1. What this is

Mangrove (mangrove.one/hackathon) ran a 36-hour online hackathon, 28–30 August 2026, on
**how local governments should respond to AI-driven catastrophic risks**. Mangrove is an AI
safety field-building organisation, not a civic-tech one — that distinction drove most of the
decisions below.

- **Tracks:** Prepare · Measure · Govern · (or propose your own)
- **Judged on:** Question and scope · Rigor and honesty · Usefulness to decisionmakers ·
  Communication to intelligent non-specialists
- **Submission:** artifacts plus a 3–5 minute video
- **Prize:** $500, feedback within a week
- **Judges:** four, spanning digital governance, AI research, economics and AI safety

**The single most important strategic point:** those judging criteria are *research* criteria,
not engineering criteria. Nothing rewards technical difficulty. Strong technical teams lose
these by shipping an impressive demo that answers no stated question and declares no
limitations. Julie's background — social work, education, lived and worked with Aboriginal and
Torres Strait Islander people in remote communities, Blue Dot and Sentient Futures AI safety
training — is the competitive advantage, not a soft supplement to it.

---

## 2. Where everything is

```
Documents/Hackathon/
├── HANDOVER.md      <- you are here
├── README.md        one-page index
├── docs/            three reference documents, open in any browser
│   ├── mangrove-hackathon-brief.html        ten project options + top three + build spec
│   ├── qld-council-governance.html          what QLD councils are, what law governs them
│   └── ai-disaster-resilience-index.html    the AI risk index framework
├── code/            6 Python scripts + questions.yaml, requirements.txt, .env.example
├── data/            ADRI already pulled, plus the complete 78-row council list
├── cache/           raw ADRI API response (12MB) so you never re-hit their server
└── research/        raw source material worth keeping
```

All scripts resolve `data/`, `cache/` and `results/` as siblings of `code/`. Keep that shape or
they will silently write somewhere else. `cache/` is regenerable — safe to delete if you want
the folder small.

The three HTML files are the durable copies. They were also published as private pages on
claude.ai — if that account is still accessible the URLs are at the end of this document, but
**do not rely on them**; the files here are the real ones.

---

## 3. The state of play

Two viable projects came out of this. Both are described in `docs/`. Neither was built.

### Option A — AI Disaster Resilience Index *(the stronger one)*

Take the **Australian Disaster Resilience Index**, a peer-reviewed, government-published index
that scores every Australian LGA on coping and adaptive capacity across eight themes, keep its
architecture, and swap the hazard from natural disasters to catastrophic AI.

**The data is already downloaded and sitting in `data/`.** See section 6.

Full framework in `docs/ai-disaster-resilience-index.html`: six catastrophic outcomes, one
scoreable exposure factor each, mapped to public LGA-level data.

### Option B — Council front-door accuracy audit

Measure what general AI assistants tell Queenslanders about their own council, scored against
the council's own website as ground truth, stratified from SEQ metro to the 17 Indigenous
councils. Code scaffold is in `code/`, described in `code/README.md`.

**Recommendation if you only do one: Option A.** It has real data in hand, a validated
architecture to borrow, and a genuinely novel question. Option B is a good fallback because it
depends on no legal analysis at all.

---

## 4. Verified findings — do not re-research these

Everything here was checked against primary or authoritative sources during the session.
Where something is uncertain it says so.

### 4.1 Robodebt: what happened to the 57 recommendations

Source: PM&C *Robodebt Royal Commission Implementation Update, March 2026*. The full extracted
text is in `research/robodebt-pmc-implementation-update-march-2026.txt`.

Three different questions, three different answers:

| Question | Answer |
|---|---|
| Accepted? | **56 of 57**, Nov 2023 |
| Reported implemented? | **52** — 51 "Implemented" + 1 "Implemented – ongoing" (23.1) |
| Still open? | **4** — 16.2, 17.1, 17.2, 18.2 |
| Needing legislation, unpassed? | **3** — 17.1, 17.2, 18.2 |

The document's own legend reads `* indicates legislation is required`.

- **The 57th** — "Section 34 of the Cth FOI Act should be repealed" (the cabinet-documents
  exemption) — was reclassified as a "closing comment" and rejected.
- **17.1** — a consistent legal framework for automation in government, with a clear review
  path, plain-language disclosure and published business rules. Still "the Government will
  consider". AGD ran a consultation paper late 2024; no Bill.
- **17.2** — a body to monitor and audit ADM for bias and fairness. Same status.
- **18.2** — repeal s 1234B Social Security Act, restore the six-year debt limitation.
  Accepted *in principle* only.

**Two of the three unlegislated recommendations are the automated-decision-making ones.**

Most of the 52 completed items were administrative — training, directions, guidance, Budget
Process Operational Rules, recordkeeping standards. The clear legislative wins rode on the
**Administrative Review Tribunal Act 2024**: the ART, publication of first-instance decisions,
the re-established Administrative Review Council, and the Ombudsman's referral powers.

### 4.2 None of it reaches local government

- All 57 recommendations are directed at **Commonwealth** entities.
- The **Privacy Act 1988 (Cth) does not apply to councils** — they are state authorities. So the
  new automated-decision transparency obligation (APP 1.7–1.9, commencing **10 December 2026**)
  binds **no Australian council**.
- State privacy Acts *do* cover councils (QLD Information Privacy Act 2009, NSW PPIPA, VIC PDP
  Act, TAS, NT; WA's PRIS Act from 1 July 2026; **SA has none at all**) — but none contains an
  ADM provision. *This last point was checked by searching, not by reading seven statutes
  clause by clause. Verify before citing.*

### 4.3 The Queensland hook that matters most

**Human Rights Act 2019 (Qld), s 9 and s 58.** Local governments and councillors are **core
public entities**. A public entity must act compatibly with human rights and **give proper
consideration to human rights when making a decision** — demonstrably, on the record.

That is, in substance, most of what Article 27 of the EU AI Act demands of a European
municipality. **Queensland has had it since 1 January 2020 and nobody applies it to automated
systems.** This is the strongest argument available: you are not importing a European regime,
you are showing what an existing Queensland duty would mean if applied to AI.

### 4.4 What Queensland councils actually do

Full detail in `docs/qld-council-governance.html`.

- Local government is **not mentioned in the Commonwealth Constitution**. Referendums failed in
  1974 and 1988. Councils are entirely creatures of state law.
- **Local Government Act 2009** governs 76 councils; **Brisbane has its own Act**, the *City of
  Brisbane Act 2010*.
- The LGA does **not enumerate functions**. Section 9 is a general competence power. What a
  council does is the residue of what the State has not kept, plus what specific Acts assign.
- **They do:** rates, waste, local roads, development assessment (Planning Act 2016), building
  compliance, parking and local law enforcement, animal management, environmental health,
  water and sewerage in most regional areas, local disaster coordination, libraries, parks,
  cemeteries.
- **They do not:** health, schools, police, public housing, child safety, welfare, public
  transport, main roads, courts. *An earlier draft of the project had councils doing housing
  referral and homelessness. That was wrong. Don't reintroduce it.*
- **Exception:** Queensland's 16–17 Indigenous councils deliver in remote communities what the
  State provides elsewhere.

**Procurement** — LGA s 104 sets five sound contracting principles; Local Government Regulation
2012 ch 6 sets thresholds. **Medium from $21,000 (written quotes), large from $280,000 (public
tender)**, raised from $15k/$200k on **12 December 2025**, CPI-indexed annually from 1 July
2026. Note: a SaaS AI tool under $21,000 a year needs no quotes at all.

**Technology** — there is **no Queensland legislation, regulation or mandatory policy** governing
council use of AI or automated decision-making. Not one instrument.

### 4.5 Why Indigenous councils cannot behave like other councils

Not scale — **tenure**. Most land in Queensland's Indigenous LGAs is held communally under
**Deed of Grant in Trust**, and under the *Land Valuation Act 2010* valuations are generally not
issued there. No valuation means no rateable value, so the ordinary revenue base of a council
effectively does not exist. Hence the **Indigenous Councils Funding Program: $74.6 million in
operating grants in 2025–26**, money that elsewhere comes from rates.

*Sources differ on whether there are 16 or 17 Indigenous local governments — Torres Shire is a
mainstream shire serving a largely Indigenous population. Pick a definition and state it.*

### 4.6 Critical infrastructure

Under the **Security of Critical Infrastructure Act 2018**, a "critical water asset" is one
serving **at least 100,000 connections**, and only then does a critical infrastructure risk
management program apply. **Almost every Queensland council that runs water and sewerage sits
below that line** — so they operate critical infrastructure that is not regulated as critical
infrastructure. This is finding H1 in the index framework.

### 4.7 The AI risk taxonomy to cite

**International AI Safety Report 2026** — published 3 February 2026, led by Yoshua Bengio, 100+
authors, expert panel nominated by 30+ countries including Australia. Three categories:

1. **Malicious use** — cyberattacks, deepfakes, biological weapons uplift
2. **Malfunctions** — hallucination, evaluation gaming, loss-of-control behaviours
3. **Systemic** — labour market disruption, threats to human autonomy

Use this rather than your own list, so nobody can say you picked risks that suited your data.

### 4.8 Australian AI policy, current state

- **Australian AI Safety Institute** — established early 2026, **$29.9m**, under DISR, testing
  unreleased frontier models as of July 2026. Remit covers upstream risks and downstream harms.
- **National AI Plan** — 2 December 2025. Nine actions. Names harms: nudify apps, scams and
  deepfakes, voice cloning, chatbots isolating teens, cyber risk. Position: **existing laws are
  the foundation**, no standalone AI Act.
- **Government response to the Senate Select Committee on Adopting AI** — tabled 1 April 2026,
  accepted *in principle* mandatory guardrails for high-risk AI.
- **Joint Select Committee on Artificial Intelligence — appointed 20 August 2026.** Examining
  risks and opportunities, **adequacy of existing laws**, national security, data sovereignty,
  consumer protection, deepfakes, cyber. **Check aph.gov.au for whether submissions are open —
  this work has a real destination if they are.**
- **Productivity Commission**, *Harnessing data and digital technology* interim report, Aug 2025
  — finds large-scale job displacement is **not** occurring and major employment effects are not
  expected for at least a decade. Useful as a source that cuts *against* a labour-shock framing.

### 4.9 Disaster management — the best document corpus in Queensland

Under the **Disaster Management Act 2003** every council must maintain a **Local Disaster
Management Plan** and a Local Disaster Management Group. All 77 have one and they are public —
a mandated, uniform, published, per-council corpus.

Better: the **Office of the Inspector-General of Emergency Management (IGEM)** already maintains
the Emergency Management Assurance Framework and the Standard for Disaster Management in
Queensland, assesses local and district plans, and tables reviews in Parliament (four in
December 2025). You would be extending an official rubric, not inventing one.

**Open question nobody has asked:** do local disaster management plans anticipate *synthetic*
warnings and impersonated official channels?

---

## 5. Corrections already made — don't loop back through these

The thesis went through several rounds of repair. These are settled:

1. **The theme is catastrophic risk, not civic tech.** A tool that makes council services nicer
   scores badly.
2. **Robodebt is a source of the failure taxonomy, not a compliance bar.** Scoring a 25-staff
   shire against a national welfare scheme's governance is a category error. Score
   *proportionality* — is the safeguard matched to the consequence of the decision this council
   actually automates.
3. **Do not propose that Australian councils adopt the EU regime.** A full fundamental rights
   impact assessment is absurd apparatus for a small shire. Borrow the classification
   *questions*, leave the compliance *machinery*.
4. **Remoteness is not monotonic vulnerability.** A town of 400 can seal entry and exit; a city
   of two million cannot. Forty staff can run rates on paper; Brisbane cannot. A fake council
   message is checkable in a small town by walking down the street. Decompose every factor into
   **exposure × (1 − absorptive capacity) × consequence** and set the sign on remoteness per
   term. Two of six hazards flip or become ambiguous, and the institutional one plausibly
   inverts entirely — a highly digitised metro council is *more* exposed than a paper-based
   shire.
5. **The Gemini API is not Google's AI Overview.** Different system, different retrieval. If you
   claim something about what people see in search, use a SERP API or capture manually, and
   declare the proxy.
6. **Don't script google.com directly.** Against their terms, and a bad look in a submission
   about responsible AI.

---

## 6. The ADRI data — already pulled, ready to use

The public site (`adri.naturalhazards.com.au`) is an Angular app with no download button, but it
is backed by a plain REST API. `code/fetch_adri.py` pulls it and aggregates SA2 → LGA.

**Already in `data/`:**

| File | Contents |
|---|---|
| `adri_lga.csv` | Every Australian LGA, all eight themes + coping/adaptive/ANDRI |
| `adri_lga_QLD.csv` | 78 Queensland LGAs, same fields |
| `adri_sa2.csv` | 2,330 SA2s nationally (source resolution) |
| `adri_sa2_QLD.csv` | 529 Queensland SA2s |
| `adri_theme_definitions.json` | Official prose definition of each theme — **quote verbatim** |
| `adri_ATTRIBUTION.txt` | The attribution line you must display |
| `councils.csv` | All 78 QLD entries: verified URL, stratum, Indigenous/ICFP flags, ADRI scores |
| `lga_profile_QLD.csv` | **The main working file** — 37 columns per LGA: population, SEIFA, Census medians, Indigenous share, council staff FTE, finances, own-source revenue share, ADRI |
| `DATA_DICTIONARY.md` | **Every column in every file explained**, with vintage and licence |

Analysis year **2024**, so it is current.

`councils.csv` strata, derived from ADRI remoteness: seq_metro 7 · regional_city 11 ·
outer_regional 16 · remote 8 · very_remote 19 · indigenous 17.

**The Queensland floor** (ANDRI, lower = less resilient): Aurukun 0.0000 · Palm Island 0.128 ·
Kowanyama 0.135 · Pormpuraaw 0.135 · Northern Peninsula Area 0.142 · Torres Strait Island 0.231.
Against Brisbane 0.708 and Sunshine Coast 0.731. **Aurukun is the national floor.**

Two cautions:

- **0.0000 is the bottom of a min–max normalised scale, not an absence of resilience.** Someone
  has to be zero. Reporting it otherwise would be wrong and, given who lives there, careless.
- **`information_access` is the theme closest to the AI hypothesis and is already the most
  extreme variable in the dataset** (Aurukun scores 0.0091). Check whether it does most of the
  work in any index you build — if so, say so rather than letting eight themes imply eight
  independent signals.

**LICENCE: CC BY-NC 4.0.** Remix and build on it non-commercially; you must acknowledge
**Natural Hazards Research Australia** (with the University of New England). Put the attribution
visibly on the page, not in a footnote.

### The validation that matters

If you build an index from the same inputs with the same assumptions, you will reproduce ADRI
with extra steps and a judge will say you rediscovered that remote communities are
disadvantaged. **The defence is a number: compute the rank correlation between your index and
ADRI's and report it as a headline result.**

- Correlation above ~0.9 → you added nothing, and the honest finding is still publishable:
  *AI risk exposure tracks existing disaster vulnerability closely enough that councils should
  reuse the resilience work they have already done.*
- Moderate correlation → the divergence *is* the finding. Name the councils that move and why.

Real sources of divergence, none with a natural-hazard analogue: **vendor concentration**
(cleanest), **system dependence / digitisation** (inverts — infrastructure is a strength in ADRI
and a liability here), **digital inclusion**, **population density** (protective for natural
hazards, inverts for contagion and sealability).

**Pre-register this before running it:** *if our index measures something new, highly digitised
metropolitan councils will rank worse on the warning and institutional factors than they do on
ADRI, and the overall rank correlation will fall below 0.9.*

---

## 7. Running the code

Six Python scripts. **Only two have been run, and those two have already produced everything in
`data/`.** The other four are scaffold for Option B, which was never started.

| Script | Purpose | Status |
|---|---|---|
| `fetch_adri.py` | Pulls ADRI off its REST API, aggregates SA2 → LGA | **Run** — produced `data/adri_*` |
| `build_councils.py` | Builds the 78-row council list, verifies every URL | **Run** — produced `data/councils.csv` |
| `fetch_lga_profile.py` | Joins ABS population/SEIFA/Census + QLD staff and finances onto the council list | **Run** — produced `data/lga_profile_QLD.csv` |
| `run_queries.py` | Puts the question set to Gemini / a SERP API, caches and archives | Never run |
| `grade.py` | Scrapes council ground truth, grades the answers | Never run |
| `validate.py` | Blind hand-labelling by both of you, then agreement stats | Never run |
| `analyse.py` | Stratified results plus a per-council report | Never run |

**If you take Option A you need neither of the last four.** The two that matter have already
done their job; the data is sitting in `data/`. Keep the others anyway for two ideas worth
reusing — see below.

```bash
cd code
pip install -r requirements.txt
cp .env.example .env                 # only needed for Option B
python fetch_adri.py --state QLD     # already run; re-run only to refresh
python build_councils.py             # already run; takes ~5 min, hits 78 sites
python fetch_lga_profile.py          # already run; ABS + QLD open data, all cached
```

`code/README.md` documents the Option B pipeline in full:
`build_councils.py` → `run_queries.py` → `grade.py` → `validate.py` → `analyse.py`.

Two things in there worth keeping whatever you build:

- **`build_councils.py` verification.** First run, "Noosa Shire Council" resolved to a travel
  site and got marked verified; "Palm Island" resolved to an unrelated business. The check now
  requires the page to mention the place *and* look like a council, treats 403 as "exists but
  blocks bots" rather than "missing", and keeps a hand-resolved `KNOWN_URLS` table for the seven
  councils no naming convention predicts. Add to that table rather than loosening the guesser —
  a wrong URL becomes wrong ground truth becomes a wrong finding.
- **`validate.py`.** If you use a model to grade model output, you must measure that grader
  against your own hand labels — blind, both of you, same seed — and report the agreement per
  category. Until you do, every accuracy number is unverified.

`data/councils.csv` is **complete**: all 78 Queensland entries — 77 local governments plus the
Weipa Town Authority, which is flagged `is_local_government = False`. Every website verified,
every row has a `stratum`, and each carries its ADRI scores so the baseline travels with the
list. Names and remoteness are sourced from the ADRI pull rather than typed by hand.

**54 of the 78 council websites return HTTP 403 to non-browser clients.** They sit behind a
web application firewall. This is recorded as `verified (blocks bots)` — the server exists and
answered, it just refuses automated clients. Do not read that as a broken URL, and *do* plan for
it: anything that needs to read council pages will hit the same wall. The script does not spoof
a browser user agent to get around it, and neither should you in a submission about responsible
AI.

---

## 8. Things that are NOT verified

Be honest about these in any submission.

- **"No state privacy Act contains an ADM provision"** — found by searching, not by reading
  seven statutes clause by clause.
- **Section numbers and thresholds** — current as at August 2026, but statute numbering is easy
  to get wrong. Check against legislation.qld.gov.au before anything appears in a submission.
- **Which Commonwealth Act delivered which Robodebt recommendation** — inferred from the response
  text in the PM&C table, not from an itemised legislative map.
- **EU AI Act Annex III commencement** — the high-risk timetable was amended and is currently
  slated for late 2027. Check before citing.
- **The six hazards in the index** — derived by mapping the international taxonomy onto council
  functions. The taxonomy is sourced; the six are not. Nobody has published a local-government
  AI hazard register. Say so.
- **Queensland staff and finance figures are 2015-16.** Every resource in the QLD comparative
  information open-data release stops there, whatever the portal's "last updated" date says.
  Current years exist only as documents on the Department's site, which blocks automated
  fetching. Columns carry their own `*_data_year` so the vintage travels with the number.
- **`staff_per_1000_residents` mixes vintages** — 2015-16 staff over 2025 population. Rough
  indicator only; recompute against 2016 ERP if it matters.
- **Full council names** — `councils.csv` derives most from a pattern (`<name> Regional
  Council`), which will be wrong for some shires and city councils. The *URLs* are verified; the
  *names* are not. Fix them from the Department's directory before any of them appear on screen.
- **ADRI LGA aggregation** — `fetch_adri.py` weights by area × share, because the population
  fields in the API payload are null. Area weighting over-weights large empty SA2s. Joining ABS
  ERP by SA2 code and swapping the weight would be better.

---

## 9. Key links

**Hackathon** — mangrove.one/hackathon

**Robodebt**
- PM&C implementation update: pmc.gov.au/sites/default/files/resource/download/robodebt-royal-commission-implementation-update-march-2026.docx
- Government response Nov 2023: pmc.gov.au/resources/government-response-royal-commission-robodebt-scheme
- Royal Commission: robodebt.royalcommission.gov.au

**Queensland**
- Legislation: legislation.qld.gov.au
- Comparative reports (current years; site blocks automated fetching, download in a browser):
  dlgwv.qld.gov.au/local-government/for-councils/resources/local-government-comparative-reports
- Open data (historical only, stops 2016–17):
  data.qld.gov.au/dataset/queensland-local-government-comparative-information-report
- QAO local government reports: qao.qld.gov.au/reports-resources/reports-parliament
- Human Rights Commission, public entities: qhrc.qld.gov.au/your-responsibilities/public-entities
- IGEM: igem.qld.gov.au
- Disaster management publications: disaster.qld.gov.au/publications
- Queensland Reconstruction Authority: qra.qld.gov.au

**Data**
- ADRI (the app): adri.naturalhazards.com.au — API endpoints documented in `code/fetch_adri.py`
- ADRI catalogue entry: catalogue.data.infrastructure.gov.au/dataset/rdh-australiandisasterresilienceindex
- ABS Data by Region (LGA): dataexplorer.abs.gov.au/vis?tm=ABS_REGIONAL_LGA2021
- ABS LGA boundaries as live layers: geo.abs.gov.au/arcgis/rest/services/ASGS2023/LGA/FeatureServer/layers
- Australian Digital Inclusion Index: digitalinclusionindex.org.au
- Closing the Gap dashboard: pc.gov.au/closing-the-gap-data/dashboard

**AI policy and risk**
- International AI Safety Report 2026: internationalaisafetyreport.org/publication/international-ai-safety-report-2026
- SOCI Act, water and sewerage: cisc.gov.au/information-for-your-industry/water-and-sewerage/legislation-regulation-and-compliance/soci-act-2018
- Parliamentary committees (check the Joint Select Committee on AI): aph.gov.au
- NSW Ombudsman ADM map (275 systems, March 2024, the only such mapping in Australia):
  ombo.nsw.gov.au

**Published copies of the three documents** — private pages on claude.ai, usable only while that
account has access. The files in `docs/` are the durable versions.
- Hackathon brief: claude.ai/code/artifact/b7c617cf-5abd-4b9c-a45a-1e2b5b4fe09f
- QLD council governance: claude.ai/code/artifact/3738ebce-8f8a-4ce4-aa1e-ea2afae81c98
- AI disaster resilience index: claude.ai/code/artifact/0ea67c19-bdda-4982-b68e-8965c4550059

---

## 10. If you pick this up cold, do this

1. Read `docs/ai-disaster-resilience-index.html` — that is the project.
2. Open `data/adri_lga_QLD.csv`. The baseline is already there.
3. Write the pre-registration in section 6 down, with a date, before you compute anything.
4. Build the six exposure factors with the three terms separated (section 5, point 4).
5. Compute the rank correlation against ADRI. Report it whatever it says.
6. Do not publish a single composite score. Publish the factors separately so a council can see
   which one drives its own exposure.
7. Attribute NHRA visibly.

The claim that survives all of it: *Australia has a government-published, peer-reviewed index of
which communities absorb shocks badly. It was built for natural hazards. Every catastrophic AI
scenario in the international literature lands through the same channels — essential services,
health access, warning systems, institutional capacity. The communities already known to be
least resilient therefore have the most to lose from an entirely new hazard class, and no one
has checked.*
