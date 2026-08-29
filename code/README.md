# Council AI Audit

**Question:** When a Queensland resident asks an AI about their council, how often is the answer
right, and does that depend on which council they live in?

**Problem:** An AI answer now sits above the council's own website in search results. The council
is still the accountable authority for its services, but the channel most people hit first is one
it cannot see, audit, or correct. This builds the missing feedback loop.

**Deliverable for a council:** here is what AI currently says about you, here are the answers that
are wrong, here are the pages causing it, fix them.

---

## Pre-registration, fill this in BEFORE running anything

Timestamp it, commit it, don't edit it afterwards. If the results contradict it, that is a finding.

- **Date/time written:**
- **Prediction 1:** Accuracy will fall with remoteness. Metro/SEQ councils will score above ___%;
  the 17 Indigenous councils will score below ___%.
- **Prediction 2:** The most common error will be (wrong-council contamination / assumed suburban
  service / stale figure / confabulation): ___________
- **Prediction 3:** `unverifiable` (council's own site does not publish it) will be highest for
  question(s): ___________
- **What would falsify this project:** ___________
- **Scoring rules:** frozen in `questions.yaml` and `grade.py` as of commit ___________

---

## Run order

```bash
pip install -r requirements.txt
cp .env.example .env    # add your keys
python build_councils.py --verify     # 1. build + verify the council list
python run_queries.py --provider gemini      # 2. run the sweep (cached)
python run_queries.py --provider serp --sample 25   # 3. real AI Overviews, subsample
python grade.py                        # 4. auto-grade against ground truth
python validate.py --n 60              # 5. hand-label a subsample, get agreement
python analyse.py                      # 6. stratified results + council reports
```

Everything is cached to `cache/` and archived to `archive/`. Re-runs cost nothing.
**Never delete `archive/`**, it is your evidence when a judge asks you to prove a finding.

---

## On automating the Google AI Overview capture

You asked whether this can be automated rather than copy-pasted. Three routes, in order of
preference:

**1. A SERP API that returns AI Overview content, use this.** Services like Serper.dev, SerpApi
and DataForSEO run the searches for you and return the AI Overview block as structured data.
They handle the querying commercially, so you are not scripting Google yourself. Costs are
trivial at this scale (hundreds of queries), and most have a free tier that will cover a
subsample. Check current free-tier limits when you sign up, they change.

**2. The Gemini API, use this too, but know what it is not.** It is cheap, reproducible and
scriptable, but it is *a different system from AI Overviews*, with different retrieval. It is a
proxy, not the thing itself. Say so out loud in the write-up.

**3. Do not script google.com directly.** Automated querying is against Google's terms, and
working around bot detection is not something to put in a submission about responsible AI. If you
want the genuine article, use route 1 or capture manually.

**Recommended split:** full 77-council sweep via Gemini API (reproducible spine) → AI Overview
capture via SERP API across a stratified 25 (validates the proxy) → 10 manual screenshots for the
video. State the proxy limitation up front; discovered by a judge it reads as sloppiness, declared
by you it reads as rigor.

---

## The methodological spine

You are using an AI to grade an AI. If you skip this step you have just replaced one unverified
system with another, and a judge on an AI safety panel will find it.

`validate.py` makes you and Julie hand-label a subsample **independently**, then reports:
- your agreement with each other (are the categories well defined?)
- the grader's agreement with your consensus, **per failure type**

That second number is the credibility of everything else in the project. Report it, including
where it is bad.

---

## Layout

```
questions.yaml      the question set, 8 per council, each tagged to a failure mode
build_councils.py   fetch + verify the 77 QLD councils, tag remoteness/Indigenous status
run_queries.py      run questions through providers, cache + archive raw responses
grade.py            auto-grade responses against scraped council ground truth
validate.py         human labelling CLI + inter-rater and grader agreement
analyse.py          stratified accuracy, error taxonomy, per-council reports
data/               council list, ground truth
cache/              raw API responses (never re-pay for the same query)
archive/            timestamped evidence: model answer + council page, side by side
results/            graded output, agreement stats, per-council reports
```
