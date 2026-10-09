# Run A, strict, on the held-out split

> The consolidated figures for the current engine are the two-run means in
> `analysis/2026-10-09-locomo-two-run-consolidated-report.md`, and the
> publishable set is `WEBSITE-FIGURES.md`. This document records run A on its
> own.

Engine `aa7daa2b9c5f190ee3f10de5b9bf4cbaee44e5a6` on branch
`bench/settle-20260930`. The strict path (`bench/core/run.py`) last changed at
`af6c96e`; the commits after it touch the offline and reporting tools only, so
this run's grading behaviour is the same throughout. Seven conversations no lever
was tuned on: conv-41, conv-42, conv-43, conv-44, conv-47, conv-48, conv-50.
1,486 questions, 1,151 non-adversarial, both arms on one ingest.

Interim: run A's matched-convention pass and run B are still to come, so there is
no spread yet and nothing here is a settled figure.

## The combined engine, width 25 with the wider extraction prompt

| | |
|---|---|
| non-adversarial | 74.8% (861/1,151) |
| all categories | 78.2% (1,162/1,486) |
| adversarial | 89.9% (301/335) |

## The extraction lever, out of sample, paired per question

| | `llm` | `llm_wide` | paired |
|---|---|---|---|
| non-adversarial | 72.11% | 74.80% | discordant 62/93, p 0.016 |
| adversarial | 88.96% | 89.85% | discordant 11/14, p 0.69 |
| single-hop | 78.90% | 83.03% | |
| multi-hop | 55.45% | 55.94% | |
| temporal | 73.78% | 74.67% | |
| open-domain | 51.43% | 52.86% | |

+2.69 points held-out, against +7.46 on the seen split the prompt was fitted to.
The held-out figure is the lever's effect; the seen one is validation on fitted
data, and the disclosure in the preregistration explains how far that fitting
went.

The gain is almost all single-hop, +4.13 points, which is what the mechanism
predicts: single-hop is one fact in one turn, and the wide prompt's contribution
is storing facts the shipped prompt discarded. Multi-hop moves 0.49 points, which
is consistent with multi-hop being limited by retrieval and reasoning rather than
by what is stored.

Discordance is high relative to the net: 155 questions change verdict to produce
a net 31. The pre-registered rule asks whether an effect exceeds the spread
between runs of one configuration, and that spread is what run B measures. Until
it exists, +2.69 at p 0.016 is significant against chance but unchecked against
run-to-run variation.

## Standing, and what it is not

Against the published figures under the corrected alignment, this run is ahead on
overall, single-hop, temporal and open-domain, and behind all three on multi-hop
(55.9% against 61.70 to 67.13). Three things that comparison is not: it is one
run with no spread; it puts Engraphy's strict figure against figures measured
under more permissive conventions and different answerer models, so the
matched-convention pass is the comparable one; and multi-hop is a genuine
deficit, not a rounding artefact.
