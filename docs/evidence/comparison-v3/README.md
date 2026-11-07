# Luna high versus Terra none: V3 reused-set comparison

Recommend retaining **gpt-6.1-terra** for this application. Luna high was cheaper
at standard token prices, but slower and substantially less reliable under the
application's exact-evidence contract. No model-default switch was made. The
application now selects the revised, versioned V3 prompt by default; V1/V2 and all
previous frozen outputs remain available. This is not a claim that V3 resolves all
model errors or that its label accuracy exceeds V2.

| Metric (all50, including failures) | Luna high | Terra none |
| --- | --- | --- |
| Category matches | 35/50 | 49/50 |
| Priority matches | 32/50 | 39/50 |
| Exact entity matches | 29/50 | 44/50 |
| Signals | 35/50 | 49/50 |
| Raw structural schema | 50/50 | 50/50 |
| Application-valid analyses | 35/50 | 50/50 |
| Exact routing decisions | 30/50 | 44/50 |
| Validation/operational failures | 15/50 | 0/50 |
| Missed escalation among expected escalations | 0 | 0 |
| Unnecessary escalation | 4 | 4 |
| Incorrect automatic destination | 0 | 0 |
| Automatic decisions | 18/50 | 23/50 |
| Latency p50 | 4.340s | 3.092s |
| Latency p95 | 8.057s | 4.079s |
| Input tokens | 61292 | 61292 |
| Output tokens including reasoning | 21601 | 8502 |
| Reasoning tokens | 11232 | 0 |
| Standard-price token estimate | $0.0169297 | $0.103802 |

Both received identical prompt/schema/messages and a25000 output cap; Luna used
high reasoning and Terra its established none setting. This compares configurations,
not equal compute. All100 API responses completed; no refusals/truncations/retries.
Luna's15 rejected analyses contained nonverbatim evidence. Raw JSON schema validity
does not imply application validity. The scorer's `schema` metric evaluates the
accepted analysis, so rejected evidence counts as an invalid analysis there. No
prediction was repaired or retried. Failed cases remain in every denominator.
One initial Luna failure lacks recorded latency: Luna percentiles use49 measured
calls, Terra50. Percentiles use nearest rank, not interpolation. Model order was
Luna then Terra, so network/provider timing is not randomized; latency is observed,
not a controlled throughput estimate.

Paired outcomes (Luna-only / Terra-only wins): category0/14, priority4/11,
entities1/16, signals0/14, application validity0/15, routing0/14. Exact case IDs,
both-pass/both-fail counts, per-case tokens/latency/failures, subsystem metrics,
split reports and conditional escalation denominators are in results.json and
model-specific *.score.json. Zero missed automatic escalation is not universal
safety: rejected analyses have no valid decision and are separately counted as
failures. Routing includes reason lists and standard destination, not merely the
final review queue. No overall perfect-score or production-quality claim.

Priority remains a weak area. Terra has11 priority mismatches and Luna18 including
its15 rejected analyses. Some labels conflict with the written plan: sparse help
is labeled Medium but plan permits Low; actionable setup can be labeled Low while
plan says Medium; uncertain possible outages can be labeled High without explicit
blockage. V3 follows the plan instead of fitting those labels. Labels/scorer were
not changed; no rubric-adjusted score hides these mismatches. Remaining model
errors also exist, including restored-service classification/priority and wrong
folder-deletion priority. See all score rows before drawing conclusions.

Codex manually compared raw summaries for both models/all100 calls to source
messages, including Luna's rejected analyses. No clear invented diagnosis, promise,
remediation or independently verified customer attribution was found. Several
summaries add explicit absence-of-context statements; Luna validation-06 says the
*reported* impact is limited to the account, which must not be read as proving no
other account is affected. Rejected summaries are not accepted application outputs.
This is assistant semantic review, not an independent human audit: no human
summary_review was fabricated, and summary_constraints/end_to_end_success remain
zero/review_needed. That zero is unreviewed-human status, not100 observed summary
hallucinations. Review limitations from the previous benchmark remain applicable.

## Budget and provenance

Previous project-accounted19.01065694 carried forward. Comparison conservative
accounting: Luna19.5070458 (includes fifteen retained full reservations of1.2925),
Terra0.8144950; project accounted39.33219774 of83. Historical6.22326144 and uncertain
11.617584 remain reserved in full. Estimated standard token prices are distinct
from retained reservations and actual billing; actual billed cost is unknown.
All reasoning output tokens are charged in estimates. No cache discounts taken.
Current pricing and API proof sources are documented in protocol.md.

freeze.json binds V3/schema/dataset/model efforts and exact source hashes. A7d969b
contains the execution harness; the documented preexisting-failure amendment
preserves its previous identity and does not change inference. Application prompt
selection wiring was separately updated/tested after execution began; it uses the
same V3 text. Old75-call evidence remains unchanged in ../benchmark-20261107.

The50-case corpus is a reused comparison set. Original final-test metrics remain
intact and cannot be combined with this new run as fresh holdout evidence. V3
changes came only from Astra's rubric/development review; no final-error-specific
prompt patch, dataset relabeling or billing arithmetic heuristic was added.
Overlapping concepts/templates, narrow development extraction coverage, single
sample per case/model, stochastic output and review limitations prevent a clean,
unbiased model-selection or production accuracy estimate. No new development
sweeps or extra inference calls were made.

174 offline tests passed, Ruff and diff whitespace clean; new tests cover Luna
high/strict arguments, reasoning counters, model bounds, paired resume, immutable
identities, history carry-forward, terminal failure retention and application V3
selection. Build reports from retained runtime with `uv run python -m
docs.evidence.comparison-v3.build_report` from repository root. Read protocol.md
before any paid reproduction; new roots must carry ALL current accounting.

See [failure stage and supplied-example mapping](failure-analysis-and-dataset.md)
for the audited source/field-level explanation of all15 Luna rejections and exact
placement of the supplied five inside the50. `luna-evidence-failures.json` retains
all28 offending excerpts (16 outer-quote-only excerpts and12 generated explanations).
