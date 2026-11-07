# Evaluation and model choice

ArcVault uses **Terra 6.1 with triage_v4**, reasoning `none`, and a 4,096-token output limit. Terra produced more usable responses than Luna in the recorded comparison. V4 uses a shorter prompt, but gives up some classification and routing quality compared with V3.

## Results

The dataset has 50 synthetic messages: 5 assessment examples, 25 development, 10 validation, and 10 test cases. Later runs reused these cases, so the results are comparisons on known data, not a fresh holdout estimate.

| Measure | Luna / V3 | Terra / V3 | Terra / V4 used by the app |
| --- | ---: | ---: | ---: |
| Application-valid output | 35/50 | 50/50 | 50/50 |
| Category match | 35/50 | 49/50 | 47/50 |
| Priority match | 32/50 | 39/50 | 40/50 |
| Exact entity-set match | 29/50 | 44/50 | 44/50 |
| Signal match | 35/50 | 49/50 | 47/50 |
| Full routing match | 30/50 | 44/50 | 41/50 |
| Median latency | 4.34 s | 3.09 s | 2.92 s |
| 95th-percentile latency | 8.06 s | 4.08 s | 4.67 s |
| Input tokens | 61,292 | 61,292 | 47,242 |
| Output tokens, including reasoning | 21,601 | 8,502 | 8,448 |

All API responses were valid JSON. Luna failed application validation on 15 cases because evidence fields contained added text rather than exact source excerpts. Failed analyses remain in the score denominators.

Luna used high reasoning; Terra used none. Both V3 runs allowed 25,000 output tokens; V4 allowed 4,096. No run was truncated. Models ran serially, and latency covers 49 Luna calls and all Terra calls. This compares the chosen configurations, not equal compute.

## Why retain V4

V4 reduced input tokens by 23% and improved priority matching by one case. It lost two category matches and three full-routing matches. The choice favors a compact prompt and lower input usage; V3 remains stronger on aggregate label matching.

For V4, none of the 23 cases labeled for review missed escalation. Four of the 27 cases labeled for automatic routing were escalated unnecessarily. All 23 actual automatic decisions had the correct destination.

The five assessment cases matched category, priority, signals, and full routing. Exact entity sets matched only one case: extra source-supported details or different excerpt boundaries count as mismatches.

## Limits and evidence

Exact entity scoring compares type, value, and evidence text. Full routing scoring includes both destinations, reasons, and derived fields. These measures are stricter than a usable entity or correct final queue.

Independent human scoring of summaries remains pending. The scorer's zero summary/end-to-end results indicate that missing review, not demonstrated hallucinations. The small, reused dataset and debatable labels limit what these scores say about production performance.

Earlier development runs and raw evidence are available here:

- [V1 baseline and V2 results](../evidence/benchmark-20261107/README.md)
- [V3 model comparison](../evidence/comparison-v3/README.md)
- [V4 results and provenance](../evidence/final-v4/README.md)
- [V4 per-case scores](../evidence/final-v4/comparison.score.json)

## Offline follow-up (issues 26 and 27)

The [derived routing report](../evidence/review-followups/routing-report.json)
compares saved V3 and V4 decisions case by case. Both have identical final
destinations on all 50 cases: zero missed escalations among 23 expected-review
cases, four unnecessary escalations among 27 expected-auto cases, and zero wrong
destinations among 23 actual automatic decisions. Thus V4 did not improve final
queue safety on this dataset. The 44/50 versus 41/50 full-routing scores also
compare standard queues and reasons; they must not be described as three extra
wrong final queues. Category and signal matches each regress from 49 to 47.

The chosen objective is compact input usage while retaining observed final-queue
safety, accepting worse aggregate category/signal/full-routing matching. This is
a tradeoff, not evidence V4 is universally superior. Recorded configuration rates
are USD 11/million input and USD 16.5/million output tokens. At those configured
rates, 14,050 fewer input and 54 fewer output tokens imply a USD 0.155441
usage estimate reduction; this is not a provider invoice or verified current price.

[Assistant review and human sheet](../evidence/review-followups/summary-review-sheet.json)
contains all 50 sources, saved summaries, required/forbidden facts, per-case
assistant verdicts and blank human fields. This is assistant review, not independent
human adjudication. Assessment-01 needs its account URL retained; development-20
adds an inferred consequence. Historical scorer results and review gates remain
unchanged. Reproduce the derived artifacts with `python3 -m evals.review_followups`.
