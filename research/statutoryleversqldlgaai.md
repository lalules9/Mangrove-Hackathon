# Statutory levers a Queensland council already holds over AI infrastructure

**Written:** 29 August 2026, from Julie's research session plus an independent verification pass
(AustLII cross-check + case-law search; direct fetch of legislation.qld.gov.au was blocked in
this session's network, so citations below are cross-checked against AustLII's consolidated text
instead — flagged per item).

**The argument this supports:** we don't need to argue Queensland councils *should* have a duty
regarding catastrophic AI risk — nothing in the literature supports inventing one (see the
literature-gap note at the end). Instead: councils already hold specific statutory powers and an
existing statutory responsibility that AI-run infrastructure now falls inside. The project's job
is to map AI-specific failure modes onto levers that already exist, not to propose new ones.

---

## 1. Disaster management — the strongest hook

**Disaster Management Act 2003 (Qld)**

| Section | What it says | Why it matters here |
|---|---|---|
| **s4A(d)** | "Local governments should primarily be responsible for managing events in their local government area." | Councils, not the State, carry primary responsibility — verified independently against AustLII's consolidated Act. |
| **s4A(e)** | District groups and the QDMC "should provide local governments with appropriate resources and support" | Confirms support flows *to* councils, doesn't replace their responsibility. |
| **s16(1)(d)** | An "event" includes "a failure of, or disruption to, an essential service or infrastructure" | **The direct hook.** An AI-caused failure of council-run infrastructure (traffic control, flood monitoring, water treatment) plausibly qualifies as an "event" under the Act's own words, with no new legislation needed. |
| **s29** | A local government **must** establish a Local Disaster Management Group — mandatory, not discretionary | Every one of the 77 councils already has this structure. |
| **s30** | Sets out the LDMG's 11 functions — planning, coordination, community awareness, resourcing, liaison with the district group | This is what "primarily responsible" requires in practice; an AI failure inside disaster-relevant infrastructure sits inside these existing operational duties. |
| **s13** | Defines "disaster" as a serious disruption requiring significant coordinated response | Sets the severity threshold an AI-infrastructure failure would need to cross to trigger the Act. |

**Verification note:** s4A(d)/(e) and the "primarily responsible" wording is confirmed independently
via AustLII's consolidated Disaster Management Act 2003 text. One inconsistency worth knowing: a
Queensland Government disaster-management resources page (disaster.qld.gov.au) cites this
principle as **"s4A(c)"** rather than (d) — likely a stale reference to an earlier version of the
Act. AustLII's current consolidation and Julie's own direct fetch from legislation.qld.gov.au both
say **(d)**. Use (d), but expect to see (c) in some older secondary sources — don't let that shake
confidence in the citation.

## 2. Planning and development approval

Councils sit inside the approval pathway for data-centre and AI-compute infrastructure siting —
land-use conditions, precinct frameworks (per the Planning Institute of Australia's guidance).
This is being partly centralised by a new federal framework (from July 2026) but local planning
scrutiny still applies alongside it.

**Lever:** conditions on planning approval — water/power demand-flexibility, siting away from
critical catchments — a concrete point where a council could impose AI-specific risk conditions
without new legislation. *Not yet independently re-verified this session — carried over from
Julie's research as stated.*

## 3. Procurement standards

Councils control what AI systems they buy and from whom, and can build risk-management,
auditability and vendor-liability requirements into contracts before deployment — the most
direct, currently-exercisable lever, needing no new legal authority.

- **Local Buy (LGAQ's procurement subsidiary)** runs a pre-qualified ICT supplier panel
  (arrangement **LB308**) covering "Emerging Technology," used across QLD, NT and Tasmania. No
  AI-specific panel exists in it yet.
- **Victoria's precedent:** the **Municipal Association of Victoria (MAV) AI Procurement
  Register** — confirmed via web search — is a curated, vetted panel specifically for AI vendors
  selling into local government, developed through consultation with councils, vendors, industry
  and academics, with published evaluation criteria. Live proof of the concentration structure
  described in section 6 below; not a Queensland instrument.
- Only **Cairns Regional Council** has a published AI-specific governance policy among the 77 QLD
  LGAs searched (see the infrastructure tracker).

## 4. General power of competence

**Local Government Act 2009 (Qld)**

| Section | What it covers |
|---|---|
| **s9** | General competence power — broadly, a council may do anything a natural person could do (subject to not breaching other law); confirmed via AustLII search summary: local government exercises power "within its local government area," may take account of Aboriginal tradition and Island custom, and can only do what the State could validly do. |
| **s262** | "Powers in support of responsibilities" — where a council is required or empowered to perform a responsibility under a Local Government Act, it has the power to do anything necessary or convenient to perform it, including the powers an individual could exercise (e.g. charging for a service). Confirmed via AustLII. |

**Lever:** this is the legal basis for a council acting on AI-infrastructure risk even absent
AI-specific legislation — e.g. adopting an AI risk policy, commissioning an audit, setting local
conditions — without needing state or federal authorisation first.

## 5. Local laws

Local Government Act 2009, Part 4 — councils can make local laws. No evidence found of any QLD
council having made an AI-specific local law. The power is analogous to how some US cities (e.g.
San Francisco's facial-recognition ban) used local ordinance power for AI-specific restriction. A
genuine, currently unused lever.

## 6. Concentration of power via procurement (the Hendrycks tie-in)

Hendrycks et al.'s "concentration of power" risk (see `docs/` catastrophic-risk material) has a
direct council-scale analogue: if most QLD councils buy AI systems through a shared panel (Local
Buy or a future AI-specific equivalent) rather than independently, that concentrates exposure onto
whichever vendors make the panel — a single point of failure across dozens of councils at once.

**Current reality, from the infrastructure tracker (`research/qld_lga_ai_infrastructure_tracker.csv`):**
the picture today is *distributed*, not concentrated — TechnologyOne/Retina Visions, HiLo, Swarco,
Itron, Iota, Honeywell, Taggle, Oracle, Nutanix each appear at different councils, no single vendor
dominates. HiLo (Sunshine Coast, Gold Coast flood monitoring) is the closest thing to a repeat
vendor. No systematic public dataset of *which* council bought *what* exists — vendor press
releases and Local Buy panel membership only show who's *eligible* to sell, not who was bought
from below the open-tender threshold.

**The finding worth stating plainly:** concentration risk here is not yet realised, but the
procurement infrastructure to create it (Local Buy, a future QLD AI panel modelled on MAV's) is
already in place. That is itself a governance-relevant fact, distinct from claiming current
concentration.

## 7. Ordinary negligence — the general-purpose backstop

Alongside the disaster-management-specific hook above, ordinary negligence law applies to any
council AI deployment regardless of whether it touches disaster infrastructure.

- **Wyong Shire Council v Shirt (1980) 146 CLR 40** — confirmed via case-law search. The
  foundational Australian authority for how a council's duty of care and breach are assessed. Key
  holding: a risk is "foreseeable" if it is not "far-fetched or fanciful" — foreseeability doesn't
  require the risk to be probable, just real. The Court found the Council negligent for a
  misleading "deep water" sign despite the low probability anyone would misread it that way. This
  is the doctrinal anchor for arguing a council should have foreseen an AI-infrastructure failure
  mode even if it seemed unlikely at the time.
- **Pabai v Commonwealth (No 2) [2025] FCA 796** — confirmed via case-law search, decided 15 July
  2025 (Wigney J). The Federal Court found the **Commonwealth** owed **no duty of care** to Torres
  Strait Islanders over climate-change harm, reasoning that emissions targets are "core policy"
  matters outside judicial review. **Important negative precedent** for any argument that
  government owes an affirmative duty to prevent diffuse, large-scale, foreseeable-but-uncertain
  harm. **Update on Julie's research:** this is a Commonwealth case, not a council case, and — not
  mentioned in her notes — **it is under appeal**: the applicants filed with the Full Federal Court
  on 11 November 2025. Cite it as "found, currently under appeal," not as final.
- **National AI Centre, "AI and Australian Law"** (ai.gov.au) — not independently re-verified this
  session, carried over from Julie's research. States negligence liability attaches "if a failure
  in risk management practices amounts to a failure to take reasonable steps to avoid foreseeable
  harm... and that failure causes the harm" — the general framework a council's AI-infrastructure
  liability sits inside, alongside directors' duties, WHS and SOCI Act exposure.

## The synthesis

Rather than arguing councils *should* have a duty regarding catastrophic AI risk (nothing in the
literature supports treating that as a settled proposition — see below), the project shows they
already have overlapping ones that AI infrastructure now falls inside:

- **s4A(d) + s16(1)(d) DMA 2003** — for AI failure inside disaster-relevant infrastructure
  specifically (flood monitoring, traffic coordination in an evacuation, water treatment).
- **Wyong v Shirt**-style ordinary negligence — for AI infrastructure generally, disaster-linked
  or not.
- **s9 / s262 LGA 2009** — the power to *act* on that risk (policy, audit, conditions) even where
  no AI-specific statute exists.
- **Procurement (Local Buy) and planning approval** — the two levers councils can exercise today
  without any new legal authority at all.
- **Local laws** — the one lever that exists but which, as far as this research found, no
  Queensland council has used for AI.

## What's confirmed as a genuine literature gap (don't try to fill it with an invented citation)

Three separate literatures exist and don't yet talk to each other: (1) ordinary negligence/duty-of
-care law applied to AI generally, (2) responsible/ethical municipal AI governance (bias,
transparency, procurement — e.g. the Maddocks Victorian survey, the ScienceDirect municipal-policy
study), and (3) national/critical-infrastructure catastrophic-AI-risk frameworks that stop at the
state or national level (CSET, HSToday, SOCI Act). Nothing found treats "local government has an
affirmative duty to reduce catastrophic AI risk" as a stated, defended proposition. That absence
is itself a citable finding, not a gap to paper over with a stretched reading of an unrelated
source.

## Things flagged as unverified — check before they go in the submission

- Planning-approval lever (section 2) and the National AI Centre negligence framing (section 7,
  last bullet) — carried over from Julie's research, not independently re-checked this session.
- The Bengio *International AI Safety Report 2026* three-category structure (malicious use /
  malfunctions / systemic risks) is independently confirmed as real and current. One secondary
  summary surfaced in verification claimed the report puts labour-market displacement at "60% of
  jobs in advanced economies" — that number does **not** match the report's own more cautious
  framing (no measurable employment effect yet, early signs only in some fields). Don't cite the
  60% figure without checking the report's primary text directly.
- Direct fetch of legislation.qld.gov.au was blocked by this session's network — all statutory
  wording above is cross-checked against AustLII's consolidated text instead, which should be
  equivalent but is a secondary republication, not the primary government source. Worth a direct
  legislation.qld.gov.au check before the submission is final, if that access is available from
  wherever the submission actually gets written.
