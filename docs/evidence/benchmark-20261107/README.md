# Frozen Terra benchmark — 2026-11-07

75 real serial Responses calls, zero SDK retries: baseline development 25, one
substantive prompt revision, development verification 25, validation 10, frozen
final test 10 once, final assessment 5. All completed and raw responses/usage were
persisted before validation. events.jsonl contains reservation, attributed raw,
returned usage, completed canonical records and append-only reconciliation events.
Original terra-network-20261107 artifacts and samples were not overwritten.

| Split/run | Category | Priority | Exact entities | Signals | Schema | Routing |
| --- | --- | --- | --- | --- | --- | --- |
| Baseline development | 24/25 | 15/25 | 13/25 | 24/25 | 25/25 | 18/25 |
| Revised development | 24/25 | 25/25 | 25/25 | 25/25 | 25/25 | 18/25 |
| Validation | 9/10 | 10/10 | 10/10 | 10/10 | 10/10 | 9/10 |
| Frozen final test | 9/10 | 10/10 | 9/10 | 10/10 | 10/10 | 9/10 |
| Final assessment | 5/5 | 3/5 | 2/5 | 5/5 | 5/5 | 5/5 |

These are small synthetic counts, not production accuracy or a perfect quality
claim. Per-case failures, full denominators, conditional escalation/automation
metrics and latency are in each score.json and execution-summary.json. No missing,
invalid or operationally failed predictions occurred. Routing equality includes
reason-list equality, not just destination. Development billing cases often remain
unresolved because component bases are absent: no new billing heuristic was added.

Final test failures: restored-service time entity extra; sparse workspace complaint
category differs from rubric and therefore its standard route differs even though
it correctly enters Human Review. Assessment exact-entity mismatches: extra `every
month`, invoice `#8821` versus annotated `8821`, and `around 2pm EST` versus `2pm EST`.
Those last two preserve source meaning but fail the deliberately exact scorer.
Final assessment priority misses are login Medium versus labeled High, and Okta
Low versus Medium. Invoice is now Medium.

Important correction: prior narrative reported original-five priority 3/5, counting
login Medium as correct. The current reviewed dataset labels login High. Rescoring
the preserved original outputs against this exact dataset gives 2/5, not 3/5;
see original-five-current-rubric.score.json. Labels and originals are unchanged.

## Accounting

reconciliation.json binds the old raw journal hash and its five usage settlements:
4738 input / 1026 output, conservative estimate 0.069047. Historical 6.22326144 and
uncertain APIConnectionError 11.617584 remain reserved in full. New 75 calls:
81054 input / 12677 output, conservative estimate 1.1007645. Combined accounted
amount is 19.01065694 against 83, including uncertainty. Actual billed cost is
unknown. Recorded rates 11/M input and 16.5/M output are retained conservative
rates, exceeding the current published Terra Standard 1/5 and Fast 2/10 rates
(including 10 percent regional uplift), verified 2026-11-07 against
https://developers.openai.com/api/docs/pricing. No cache discount was taken.

Each new call reserved the unchanged full-context maximum 11.617584 before the
network request. Only completed calls with complete valid bounded usage and the
requested model release excess. Missing/invalid usage retains maxima; unresolved
attempts block resume. Append-only reconciliation is idempotent and serialized by
exclusive lock. Baseline, development, validation, test and assessment share one
journal, accounting config and lock. The approved credential was read only inside
consuming shell commands; no credential enters these artifacts.

## Identities and summary review

freeze.json and test/assessment manifests identify frozen prompt/schema/dataset
and exact application/eval source hashes at code f25c59d. Prompt v2 is an opt-in
benchmark selection; the ordinary application's default remains v1. Earlier v2
development/validation exports carry the provider's old fixed v1 display label;
reserved inference hashes and manifests bind their actual v2 text. Before final
test, export provenance was corrected to the selected prompt stem and hashes.
Baseline and development ran during runner construction, not from a pristine
commit: their manifests record the starting commit; reservation hashes bind exact
prompt/schema. Validation and final manifests include source hashes. No stronger
clean-checkout provenance is claimed for development runs.

Codex manually compared all 75 summaries with their source messages and annotated
facts after each split completed. No clear unsupported diagnosis, promise or
remediation was observed. Development-20's 'risks destructive data loss' is an
inference from wrong-folder deletion, not a verified loss report. Sparse summaries
explicitly mention missing context. Final assessment summaries preserve customer
attribution, monetary figures and outage timing; login mentions an account URL
without repeating it (the entity retains it). This is assistant review, not an
independent human faithfulness audit. No human summary_review was fabricated:
scorer summary_constraints/end_to_end_success remain zero with review_needed.

Dataset review is recorded in evals/review.jsonl; earlier pending-review wording
in evaluation.md predates those records. Families are separated by split, but
billing threshold templates and outage concepts overlap semantically. Development
has 24 expected-empty entity sets and only one time entity; its improvement does
not establish identifier generalization. Final test was first inspected here only
after its frozen execution; no prompt changes followed.

## Astra post-freeze review

Astra reviewed only prompt/specification and development labels/evidence. Findings:
priority definitions conflict between plan and v2 (sparse inputs, suspected outage,
setup guidance); active broad-outage category precedence is implicit; entity scope
omits explicit error-code guidance; equal-intent labels impose an unstated Billing
tie-break; nonnumeric discrepancies and generic refund requests need clearer
boundaries; development extraction coverage is narrow; quoted/hypothetical attack
coverage is incomplete. These are valid follow-up specification/coverage concerns,
not grounds to relabel or tune the frozen test. No further prompt revision was made.

## Reproduction and verification

Use Python 3.14 via uv; set UV_CACHE_DIR=/tmp/arcvault-uv,
UV_PROJECT_ENVIRONMENT=/tmp/arcvault-benchmark-venv, explicit SQLite DATABASE_URL
and synthetic DJANGO_SECRET_KEY for offline checks. `uv run pytest -q`: 169 passed
(six existing missing-staticfiles warnings). Ruff and git diff --check passed.
Regression checks cover unknown/missing usage, idempotent reconciliation, serial
budget release/exhaustion, raw evidence attribution, phase ordering, freeze and
completed final-test resume without duplicate calls.

Dry run (no credential):

```
uv run python manage.py run_benchmark --run-dir .acceptance-runtime/new-benchmark --config config/acceptance/benchmark.json --phase baseline
```

Execution additionally requires OPENAI_API_KEY and --execute. Run baseline with
v1, then development and validation with --prompt prompts/triage_v2.txt. Freeze
using validation --freeze (no API call), then run test and assessment with that
prompt. This authorizes no additional paid reruns by itself: carry forward ALL
existing accounted costs/reservations in a new config before starting another run.
For restarting the retained live journal, use frozen checkout f25c59d: immutable
phase identities intentionally reject a changed Git head. Review reports offline:

```
python3 -m evals.score score docs/evidence/benchmark-20261107/test.predictions.json --split test --unlock-test
```

No queue/Postgres/provider billing statement, production deployment, independent
human summary acceptance or submission readiness is claimed by this benchmark.
