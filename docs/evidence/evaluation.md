# Offline evaluation revision — 2026-11-07

Reviewed starting head: b24d5f90dfd8ca8e76397b1517c18274b4ad95c1.
All five assessment message strings were checked as exact substrings of the original
attached DOCX text. No live calls, spend, prompt tuning or model benchmark occurred.

The 45 generated cases were replaced with scenario groups assigned before splitting:
25 development, 10 validation, 10 refreshed final test, plus 5 assessment.
Families and minimal pairs stay together. Coverage includes injection, competing
intent, sparse requests, active/resolved/historical/negated/unresolved outages,
USD threshold pairs, undercharge, currency and period/component mismatches.
Final test was inspected for harness construction only. Freeze configuration before
`--unlock-test`; do not tune prompts on it. Independent reviewers may audit it.
All changed labels and entity/fact annotations are pending independent review;
previous approval of old simple labels does not approve this replacement set.

Entities now have explicit expected-none versus annotated status, type/value/exact
evidence. Exact-set scoring penalizes omitted entities and unsupported extras;
missing/invalid analyses cannot earn extraction credit. Equivalent entity spans
may need human adjudication. Time expressions and relevance completeness remain
part of the pending annotation audit.

Summary annotations are source-derived fact units, not text the model must copy.
They require independent refinement where compound statements remain. No lexical
match claims semantic correctness. Every prediction starts review-needed. A human
must supply `summary_review` with a nonempty `reviewer`, `all_required_facts: true`
and `no_unsupported_claims: true` after comparing every annotated fact and every
summary claim against the source. This is caller-supplied judgment, not authenticated
review provenance. Paraphrases can pass; omissions and hallucinations must fail.

Reports include full-population missing, operational-error, invalid-analysis,
completion and end-to-end-success counts. Every aggregate retains the full case
denominator. Conditional routing separately reports missed escalations among valid
automatic decisions requiring escalation, unnecessary escalations among valid
escalated decisions, and wrong destinations among automatic decisions. Zero
conditional denominators mean undefined rates, never success. Routing counts do
not replace end-to-end success; failures remain visible. Schema validation remains
structural, not application semantic/evidence validation.

Verification:

```
python3 -m unittest discover -s tests -v
# 7 passed: dataset, leakage, independent paraphrase, omission/hallucination,
# missing/extra entities, missing/invalid/error predictions, duplicate IDs.
python3 -m evals.score validate
# 50 draft cases validated
```

Use `python3 -m evals.score score predictions.json --split development`.
No measured model quality, cost, latency or production behavior is claimed.

## Bounded follow-up

Verified starting PR head 1ede301cc84a7d6719605fc62b3caf7dfa1dce65.
Focused verification: 10 unittest tests pass; dataset validation passes.
No live benchmark was run. Annotation review remains pending; this is not a
completed independent 50-case semantic audit or application export integration.
Main integration and full application suite/Ruff remain outstanding.

Review traceability (https://github.com/ahnaineh/arcvault-ai-triage/pull/1):
- #discussion_r4501457049: missed-escalation denominator now includes every
  expected escalation, including missing predictions; test_review_denominators.
- #discussion_r4501457052: unnecessary-escalation numerator now requires valid
  analysis, matching the denominator; test_review_denominators.
- #discussion_r4501457055: assessment-05 requires onset 2pm EST;
  test_assessment_onset.
- #discussion_r4501441540: malformed analysis examples remain reportable;
  test_malformed_fields. Malformed summary_review and decision values are guarded.

The earlier paragraph defining the missed-escalation conditional denominator is
superseded by the all-expected-escalations definition above.
