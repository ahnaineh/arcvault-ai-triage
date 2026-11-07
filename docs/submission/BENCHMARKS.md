# Benchmarks and model choice

**Choice: Terra 6.1 with the compact V4 prompt.** Terra followed the evidence contract more reliably than Luna and scored better on classification, entities and routing. V4 keeps the prompt short; it is a tradeoff, not an across-the-board quality improvement over V3.

## What was tested

The dataset contains **50 synthetic cases: 5 assessment examples, 25 development, 10 validation and 10 test cases**. Classification, priority, entities, signals and routing are scored separately. Failed analyses stay in the denominator.

| Stage | Configuration | Calls | Purpose |
| --- | --- | ---: | --- |
| Initial baseline | Terra / V1 | 25 | Find development weaknesses |
| First revision | Terra / V2 | 50 | 25 development, 10 validation, 10 frozen test, 5 assessment |
| Model comparison | Luna high / V3 and Terra none / V3 | 100 | Same 50 messages, prompt and schema for each model |
| Final compact prompt | Terra none / V4 | 50 | Check the shorter prompt on the same 50 cases |

These stages contain **225 benchmark calls**. Schema probes and demo calls are separate. Later comparisons reused the test cases, so they are not fresh holdout results.

## Initial prompt development

| Run | Category | Priority | Exact entities | Signals | Valid analysis | Full routing |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| V1 · development baseline | 24/25 | 15/25 | 13/25 | 24/25 | 25/25 | 18/25 |
| V2 · development | 24/25 | 25/25 | 25/25 | 25/25 | 25/25 | 18/25 |
| V2 · validation | 9/10 | 10/10 | 10/10 | 10/10 | 10/10 | 9/10 |
| V2 · frozen test | 9/10 | 10/10 | 9/10 | 10/10 | 10/10 | 9/10 |
| V2 · assessment | 5/5 | 3/5 | 2/5 | 5/5 | 5/5 | 5/5 |

Development gains were strongest in priority and entities. The development set had limited identifier variety, so those gains alone did not prove broader extraction quality.

## Why Terra instead of Luna

Both models received V3 and a 25,000-token output cap. Luna used high reasoning; Terra used none. This compares the configurations used in the app experiment, not equal compute.

| Measure | Luna · high | Terra 6.1 · none |
| --- | ---: | ---: |
| Application-valid analysis | 35/50 (70%) | 50/50 (100%) |
| Category match | 35/50 (70%) | 49/50 (98%) |
| Priority match | 32/50 (64%) | 39/50 (78%) |
| Exact entity-set match | 29/50 (58%) | 44/50 (88%) |
| Signal match | 35/50 (70%) | 49/50 (98%) |
| Full routing match | 30/50 (60%) | 44/50 (88%) |
| Evidence-validation failures | 15/50 | 0/50 |
| Median latency | 4.34 s | 3.09 s |
| 95th-percentile latency | 8.06 s | 4.08 s |
| Input tokens | 61,292 | 61,292 |
| Output tokens, including reasoning | 21,601 | 8,502 |

All 100 API responses were structurally valid JSON. Luna failed application validation on 15 because it added quotation marks or explanations to fields requiring exact source excerpts. Those failures are included above; the table measures usable application output, not just raw classification ability. No outputs were repaired or retried.

Terra therefore offered the stronger combination of usable results and observed speed. Latency uses 49 measured Luna calls and 50 Terra calls; models ran serially rather than in randomized order.

## V3 versus the final compact V4

Both columns use Terra, reasoning none, on the same 50 cases. V4 is 277 words and uses a 4,096-token output cap; V3 used 25,000. Neither run was truncated.

| Measure | V3 | V4 · final |
| --- | ---: | ---: |
| Application-valid analysis | 50/50 (100%) | 50/50 (100%) |
| Category match | 49/50 (98%) | 47/50 (94%) |
| Priority match | 39/50 (78%) | 40/50 (80%) |
| Exact entity-set match | 44/50 (88%) | 44/50 (88%) |
| Signal match | 49/50 (98%) | 47/50 (94%) |
| Full routing match | 44/50 (88%) | 41/50 (82%) |
| Median latency | 3.09 s | 2.92 s |
| 95th-percentile latency | 4.08 s | 4.67 s |
| Input tokens | 61,292 | 47,242 |
| Output tokens | 8,502 | 8,448 |

V4 used **23% fewer input tokens** and improved priority by one case. It lost two category matches and three full-routing matches, while entity matches and output validity stayed unchanged. V3 remains stronger on aggregate label matching; V4 was retained for the requested compactness, with this tradeoff disclosed. No further tuning followed the final run.

## Final routing and the five assessment cases

| V4 routing check · all 50 cases | Result |
| --- | ---: |
| Missed required escalations | 0/23 |
| Unnecessary escalations | 4/27 |
| Wrong destination among automatic decisions | 0/23 |

For the **five supplied inputs in the final benchmark**, category, priority, signals and full routing each matched **5/5**. Exact entity sets matched **1/5**: additional source-supported entities or different excerpt boundaries still fail the strict scorer. The invoice has an apparent $260 difference with explicit assumptions; the outage goes to Human Review.

## How to read the scores

- **Exact entities** requires the complete annotated entity set to match; extra or differently bounded entities count as mismatches.
- **Full routing** includes the normal queue, final queue, escalation reasons and derived fields. It is stricter than getting the final queue right.
- **Summary quality** has no independent human score yet. Machine reports show an unmet review gate, not evidence that every summary is wrong.
- The set is small, synthetic and reused. Some priority labels are debatable, and related scenarios overlap. These results support a configuration decision, not a production accuracy guarantee.

## Evidence

[Initial baseline and V2 split results](../evidence/benchmark-20261107/README.md) · [Paired V3 results](../evidence/comparison-v3/README.md) · [Luna evidence failures](../evidence/comparison-v3/failure-analysis-and-dataset.md) · [Final V4 results](../evidence/final-v4/README.md) · [Final per-case scores](../evidence/final-v4/comparison.score.json)
