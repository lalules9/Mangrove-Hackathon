# QAIRI: Project write-up

## What we set out to do

Queensland already has a peer-reviewed, government-published index that scores every local
government area for how well it copes with a natural disaster: the Australian Disaster
Resilience Index. Nobody had built the equivalent for AI. We set out to fix that, at LGA
level, using real data, not a hypothetical scenario.

The idea was simple. Take a validated architecture built for one hazard and apply it to a
different one. Not swap the hazard and call it done, but work out which parts of that
architecture actually transfer to AI risk, and be honest about what has to be built from
scratch.

## What we did

We built six scored components: essential services, population vulnerability, institutional
capacity, deployment evidence, synthetic warning, and labour market exposure. Every risk
category comes from a named source, the International AI Safety Report 2026 and Hendrycks'
Overview of Catastrophic AI Risks, not a list we invented ourselves. A hazard only made it into
the index if it traced to that taxonomy, landed through a channel local government actually
controls, varied measurably across councils, and gave a council something it could act on.

Every input is real public data: ABS Census, SEIFA, the Queensland comparative information
report, Queensland Reconstruction Authority disaster funding activations, the Mobile Black Spot
Program, Ergon's isolated network list. ADRI itself is held out of the model entirely and used
only as a comparison, never as an input, so we could not accidentally rebuild it and call it
new.

We grounded the legal reasoning in the actual Acts, not a general claim. The Disaster
Management Act 2003 already treats a failure of essential services as an event a council is
responsible for. The Human Rights Act 2019 already requires councils to give proper
consideration to human rights before making decisions. Both citations were checked directly
against the current legislation, not a secondary summary.

Everything is published as an interactive map with adjustable weight sliders, a methodology
page, a limitations page, and a legal background page, all cross-linked, all live on GitHub
Pages.

## What we found

QAIRI and ADRI rank councils differently. Spearman correlation between the two is -0.408, well
below the threshold that would mean we had just rebuilt ADRI with extra steps.

Highly digitised metropolitan councils rank worse on QAIRI than on ADRI. System dependence is a
strength when the hazard is a flood and a liability when the hazard is AI. Townsville, Brisbane,
Sunshine Coast, Moreton Bay and Livingstone all shift more than fifty ranks worse than their
ADRI position would predict.

Communities already at the bottom of ADRI carry a second, separate risk under QAIRI. They are
not just repeating the same result under a different name.

Most of the index measures general vulnerability, not a mechanism specific to AI. Of the six
components, only synthetic warning genuinely depends on AI as the cause. We say that plainly
rather than overselling the rest.

## What we would do next

Get current Queensland council staff and finance figures. Everything we have is 2015 to 2016,
because that is the most recent year available as open data.

Cross-validate the labour market exposure proxy against a second published AI-exposure measure.
Right now it is one judgement call about which occupations count as exposed.

Measure vendor concentration properly. The one data source we tried had no variance across all
78 councils. This would mean reading each council's published contract register by hand.

Finish the AI policy scan. 47 of 78 council websites have been checked; the remaining 31 are
disproportionately small, remote councils.

Switch ADRI's own LGA aggregation from area-weighted to population-weighted, since the public
API does not publish population at SA2 level and area weighting over-weights large, empty
areas.
