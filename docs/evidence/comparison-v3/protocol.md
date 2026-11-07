# Paired application model comparison protocol

User authorized Luna HIGH versus Terra and prompt fixes. Official API model page
https://developers.openai.com/api/docs/models/gpt-6-luna was read 2026-11-07:
exact public API ID gpt-6-luna; high reasoning supported; context1050000;
max output128000; Responses and Structured Outputs supported. Current model and
pricing pages list standard input/output .1/.5 per million for Luna and1/5 for
Terra. https://developers.openai.com/api/docs/pricing also lists Fast .2/1 Luna,
2/10 Terra, with10% regional uplift. Bounds use maximum context1050000 and cap25000;
Luna accounting reserves conservative1.1/5.5 per million, Terra11/16.5. These
conservative rates differ from standard-price token-derived comparison estimates.
Both figures are estimates, never actual billed costs; output includes reasoning.

V3 addresses Astra specification/development findings only. It follows the plan's
priority definition rather than tailoring to conflicting sparse/possible-outage
labels, states active outage category precedence, includes error codes, treats
current requested action generally, and uses a first-mentioned tie-break rather
than a hidden Billing preference. Discrepancies without amounts remain extractable;
refund requests alone do not imply disputed charges. No dataset/scorer or billing
policy changes. Original V1/V2 prompts and frozen scores remain intact.

All50 existing cases are paired on identical V3/schema/messages/scorer: Luna high
versus Terra none (the established Terra setting). Output cap25000 for both includes
reasoning. This compares deployment configurations, not equal reasoning effort or
equal compute. Existing test labels/results were exposed previously: the entire
set is a REUSED COMPARISON SET, not a new holdout or unbiased model-selection
estimate. No tuning from previous final-test errors. Development coverage remains
narrow; do not infer broad production accuracy. Original75 evidence remains at
../benchmark-20261107.

Root comparison.lock serializes both model ledgers. Previous known usage1.1698115
and uncertain reservations17.84084544 carried forward. Prior model accounted
amount feeds the next model's immutable history. Every attempt reserves before
calling, SDK retries disabled. A rejected application response remains a failed
prediction: no cleanup, retry or replacement. Its maximum reservation is retained.

The fifth Luna response contained nonverbatim quotation marks in outage evidence
and failed application validation. The original runner stopped. An explicitly
recorded harness amendment added terminal failure records/continuation; prompt,
models, schema and dataset identities stayed unchanged. Four completed Luna calls
were reused; the fifth raw response was converted into an error record without
another API call. Original and amended code identities are retained in
harness-amendment*.json. This is a harness fault-handling correction, not model
output repair. First failure latency was not durably recorded by the old failure
event; it is missing, not imputed. Subsequent failure events retain measured latency.

Offline regressions verify Luna high/strict request, reasoning usage retention,
full-context pricing floors, paired resume without duplicate calls, immutable
freeze rejection, carried-forward history and terminal failure reservation retention.

After execution started, application wiring was updated to select V3 by default
via OPENAI_PROMPT_VERSION (allowlisted V1/V2/V3), retaining Terra as model default.
The running comparison process had already loaded the frozen harness at a7d969b;
explicit prompt overrides sent V3 to both models. Application wiring changes are
separately tested and do not change any recorded request or justify reusing this
set as an unseen holdout. To resume this exact frozen ledger, use checkouta7d969b
or explicitly audit/record a harness-only amendment; inference changes are rejected.

Reproduce offline with explicit SQLite DATABASE_URL, synthetic DJANGO_SECRET_KEY,
UV_CACHE_DIR=/tmp/arcvault-uv and UV_PROJECT_ENVIRONMENT=/tmp/arcvault-benchmark-venv:
`uv run pytest -q` (174 passed; six existing staticfiles warnings), Ruff clean.
`uv run python manage.py compare_models --run-dir .acceptance-runtime/new --execute`
is the comparison command, but starting another paid run requires carrying forward
ALL costs/reservations in its history (hardcoded prior benchmark checkpoint alone
would omit this comparison). No additional rerun is authorized by this example.
Use the existing ledger for safe resume; never copy it to a new empty accounting
root as a way to reset spend. Credential is supplied only by the consuming process.
