# What powers councils already hold — and the sources behind them

Compiled from Julie's research, with validation notes. **Verify each citation against the
primary instrument before it appears in a submission** — several are marked unverified.

## The reframe that makes this work

Nothing in the literature supports arguing councils *should* have a duty regarding catastrophic
AI risk. You don't need to. **They already have duties that AI infrastructure now falls inside.**
The novel contribution is mapping AI-specific failure modes onto powers that already exist.

## Five levers

| # | Lever | Instrument | Status |
|---|---|---|---|
| 1 | **Planning and development approval** — conditions on data-centre and AI-compute siting, water and power demand | Planning Act 2016 (Qld) | Being partly centralised by a federal framework from July 2026 — check currency |
| 2 | **Procurement** — risk management, auditability and vendor liability written into contracts before deployment | LGA 2009 s 104 sound contracting principles; LG Regulation 2012 ch 6 | **The most directly exercisable lever. Needs no new authority.** Verified |
| 3 | **General competence** — power to do anything a natural person could, so a council can adopt an AI risk policy or commission an audit without state authorisation | **LGA 2009 s 9** (and s 262) | s 9 verified |
| 4 | **Local laws** — Part 4 LGA 2009. No QLD council has made an AI-specific local law; the power exists. Precedent: San Francisco's facial-recognition ordinance | LGA 2009 Part 4 | Power verified; the "none exist" claim is unverified |
| 5 | **Statutory disaster-management role** — councils are **primarily responsible** for disaster management in their LGA, via a mandatory Local Disaster Management Group | **Disaster Management Act 2003 (Qld) s 4A(c)**, Part 5 | LDMG duty verified. **s 4A(c) specifically NOT verified — read the section** |

**Lever 5 is the strongest hook.** If a council runs AI inside flood monitoring, evacuation
traffic coordination or water treatment, an AI failure sits inside a pre-existing statutory
duty. Nothing novel needs inventing.

## Liability scaffold

- **Wyong Shire Council v Shirt (1980) 146 CLR 40** — foundational Australian case for how
  council duty of care and breach are assessed. The doctrinal anchor.
- **Pabai v Commonwealth (2025)** — the Federal Court declined to find the Commonwealth owed a
  duty of care to Torres Strait Islanders over climate harm. **Important negative precedent**:
  a court has already refused to extend duty of care to diffuse, large-scale,
  foreseeable-but-uncertain harm. Anyone claiming an affirmative duty over catastrophic AI harm
  meets this first.
- **National AI Centre, "AI and Australian law"** (ai.gov.au) — negligence attaches where a
  failure in risk management amounts to failing to take reasonable steps against foreseeable
  harm. Also flags directors' duties, WHS, privacy and SOCI.
- *Locating Fault for AI Harms* (Journal of Media Law, 2025) — assigning fault across the AI
  value chain: developer, deployer, operator.

## Concentration of power — the Hendrycks angle

- **Local Buy (LGAQ's procurement subsidiary), arrangement LB308** — pre-qualified ICT panel
  including "Emerging Technology", used across QLD, NT and Tasmania. If most councils buy AI
  through a shared panel, exposure concentrates onto whoever makes the panel. *Arrangement
  number unverified.*
- **MAV AI Procurement Register (Victoria)** — a dedicated vetted AI vendor panel with published
  criteria. The closest live precedent for that concentration structure. Queensland has no
  equivalent yet.
- Current QLD picture is **distributed, not concentrated**: TechnologyOne/Retina Visions, HiLo,
  Swarco, Itron, Iota, Honeywell, Taggle, Oracle, Nutanix all appear across different councils.
  HiLo is the only repeat (Sunshine Coast and Gold Coast flood monitoring).
- **Not compiled anywhere as a dataset.** Vendor press releases plus Local Buy panel membership
  is all that exists publicly, and panel membership shows who *may* sell, not who bought.

## Taxonomy sources — read in this order

1. **Hendrycks, Mazeika & Woodside (2023)**, *An Overview of Catastrophic AI Risks*,
   arXiv:2306.12001 — malicious use / AI race / organisational risk / rogue AI.
2. **Bengio et al., International AI Safety Report 2026** — malicious use / malfunctions /
   systemic risks. Verified: published 3 Feb 2026, 100+ authors, 30+ countries.
3. **Kasirzadeh**, *Two Types of AI Existential Risk: Decisive and Accumulative*,
   arXiv:2401.07836 — **the most useful for LGA framing.** Council-level risk is
   *accumulative* (a vendor platform failing across many LGAs), not decisive.
4. **Slattery et al., The AI Risk Repository** (MIT FutureTech) — 1,725 risks from 74 sources.
   Use as a cross-check, not a narrative.
5. **Pouresmaeil, Afroogh & Jiao**, arXiv:2502.16644 — AI-caused disasters and government
   accountability. The closest paper to this project.

## Empirical baseline

- **Maddocks (2026), *Bridging the Gap*** — 337 officers across 75 Victorian councils,
  **two-thirds using AI with no governance in place.** The defensible baseline claim.
- **MDPI *Systems* (2026)**, PRISMA review — the only source using "systemic risk" language at
  municipal AI level.

## The gap, stated

No paper frames local government as having an affirmative duty to reduce *catastrophic* AI risk.
Three literatures exist and none of them meet: negligence law applied to AI; responsible
municipal AI governance (bias, transparency, procurement); and national critical-infrastructure
catastrophic-risk frameworks that stop above the local tier. **That absence is itself a finding.**

## Two counting discrepancies to resolve

- The "Confirmed AI (8)" tally lists **nine** councils (Brisbane, Moreton Bay, Sunshine Coast,
  Gold Coast, Logan, Noosa, Cherbourg, Livingstone, Townsville).
- The 77-LGA regional list **includes Weipa Town Authority**, which is not a local government.
  Our dataset treats it as a 78th entity, flagged `is_local_government = False`. Pick one
  convention and state it.
