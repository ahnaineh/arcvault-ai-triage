# Where Luna fails and where the supplied five belong

## Audit of retained runs

Checked the committed journals against reports on2026-11-07. The original75-call
benchmark has75 unique reservations,75 raw responses and75 terminal records. The
paired comparison has100 of each (50/model), including15 explicit Luna failures.
No failed case was resent. The source journal hash in the original-five
reconciliation still matches; original raw evidence was not rewritten. Full
reports, exact prompt/schema/code/data identities, model efforts, bounded caps,
per-case usage, paired changes, latency percentiles and accounting are retained in
this directory and ../benchmark-20261107. Failed raw predictions are retained in
events.jsonl even when their exported accepted analysis is null.

`audit_evidence.py` regenerates `luna-evidence-failures.json` from the retained
Luna raw journal and dataset. Each failure record contains the case/request/provider
response IDs, source message, exact failing JSON field paths and returned excerpts.
The audit does not modify a prediction or rerun inference.

## Failure stage and responsibility

The call path is Responses API -> raw response/usage persisted -> JSON parsing ->
`validate_analysis(..., message)` -> `Analysis.evidence` in
apps/triage/schemas.py -> canonical export and policy decision.

All100 comparison responses report completed status and satisfy the structural
JSON schema. No connection error, refusal or token truncation caused these15
Luna failures. The validator rejected Luna's generated evidence because it was not
a literal substring of the customer's message. The provider wraps this as
`provider_invalid`; this label includes application-validation failure, not just
invalid JSON or an API fault. Routing is not accepted for a rejected analysis.

Across15 cases,28 evidence fields are nonverbatim:16 match after removing outer
curly quotes, and12 are explanatory/generated text rather than source excerpts.
Six cases contain only the outer-quote problem; nine have explanatory text or a
mixture. Removing quotes is only a diagnostic in the audit, never an output repair.

Example assessment-05:
- Source contains `dashboard stopped loading`.
- Luna's evidence string is `“dashboard stopped loading”`, including curly quotes
  absent from the source; it also quotes `“Multiple users affected.”` similarly.
- JSON syntax is valid and its outage category may be sensible, but the evidence
  contract is violated and the whole analysis is rejected.

Example development-02:
- Source: `All employees could not open the dashboard; service is restored.`
- Luna supplies insufficient-information evidence:
  `No current impact or requested follow-up is stated.`
- That may describe an interpretation of the input; it is not a source quotation.
  Explanations belong outside evidence fields, or the evidence list should be empty
  when no source excerpt supports a negative/absence observation.

This is a model-output/instruction-following failure under this prompt, model and
reasoning setting. The application validator is enforcing the intended exact-source
contract; strict JSON Schema cannot ensure a generated string occurs in a separate
input. Terra complied on all50 in this one paired run. This does not establish an
inherent Luna defect across prompts/tasks, nor does it prove every rejected Luna
classification or summary was semantically wrong. The accepted-analysis metric
intentionally counts the full rejected record as failed; it should not be described
as15 independently demonstrated category errors.

There was also a harness limitation: the runner initially stopped on the first
invalid response. A documented harness-only amendment allowed terminal failure
records and continuation without retrying it. That fixed benchmark execution; it
did not cause, erase or repair Luna's nonverbatim evidence. Application validation
was not relaxed. All15 failed reservations remain fully retained in accounting.

## The supplied five are inside the50

The dataset is one JSON array in evals/dataset.json. Its first five records are the
five supplied assessment messages, not five extra records outside the dataset.
Source and message strings were compared byte-for-byte with
apps/intake/sample_data.py's sample loader; all five match.

| Array row (1-based) | Case ID | Supplied example |
| --- | --- | --- |
| 1 | assessment-01 | 403 login / account URL / last Tuesday |
| 2 | assessment-02 | Bulk audit-log export request |
| 3 | assessment-03 | Invoice8821,1240 versus980 monthly |
| 4 | assessment-04 | SSO with Okta setup question |
| 5 | assessment-05 | Dashboard outage around2pm EST, multiple users |

Split sizes: assessment5 + development25 + validation10 + test10 =50. Prompt
refinement used rubric/development evidence; these five are retained acceptance
examples, not an unseen test split. They were run at the end of the original75-call
sequence with V2, and once/model as part of each50-case V3 comparison. Their earlier
five live Terra responses also remain preserved separately. Repetition is disclosed;
these are not independent new samples each time they are executed.

Their paired V3 predictions and metrics are in each model's predictions.json and
assessment.score.json. Luna's assessment-05 is the one rejected supplied example;
its raw response is still in the Luna journal and the field-level failure audit.
The previous frozen V2 five-output artifact remains in
../benchmark-20261107/assessment.exports.json; it is not overwritten by V3 results.
