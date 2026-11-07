# Live acceptance — 2026-11-07 UTC

Incomplete. Code main 16caaf3f83ed1d36fd72ecb0cf56540a30ed10e0.
Model gpt-4.1-mini-2025-04-14. Official support/pricing checked:
https://developers.openai.com/api/docs/models/gpt-4.1-mini
Standard input $0.40/M; output $1.60/M tokens.

One synthetic schema probe completed (ledger includes actual response): 935 input,
158 output tokens; estimated pre-credit $0.0006268. Output cap 1800; timeout 35s.
Five additional actual supplied messages were processed using merged load_samples,
existing image arcvault-review-sol-3-web:latest, synchronous process(), disposable
SQLite persistence and real OpenAI provider. Dispatch was suppressed. No queue or
PostgreSQL acceptance is claimed. Sample 1 failed; samples 2–5 completed. Guarded
export correctly rejected incomplete results. No assessment_outputs.json is published.

Execution defect: the disposable container was removed after export failed before
attempt ledger export. Its SQLite database was ephemeral; those five attempts'
usage, error details and records were lost. Their costs are UNKNOWN, not zero.
No repeat calls were made. The exact known subtotal is $0.0006268; total spend
cannot be determined from retained evidence. A $3 hard cap was not implemented
for the pipeline calls, whose existing adapter has no output-token cap. This run
therefore does not establish budget or sample acceptance. No credentials were
printed or copied into repository artifacts.

Pending: durable attempt ledger before export, explicit adapter output cap,
inspect sample 1 failure, five complete persisted outputs and manual review,
real Redis/Celery/Postgres acceptance, benchmark and clean-start verification.
No application code changed; no test success is claimed for this evidence-only run.

## Recovery inspection — 2026-11-07

Prepared recovery checkout fetched PR8 and verified full head
`6dc27e8626f8fda909eae69acac59545dfc7806c`. No inference or retries were
performed. `/tmp/arcvault-live.py` survives: it exports all samples before writing
`docs/evidence/live-sample-attempts.json`, confirming the failure ordering above.
No credential file was opened. `/tmp/arcvault-samples-check.sqlite3` contains no
triage tables. Read-only inspection of `/tmp/arcaccept.sqlite` found four results,
all with provenance model `mock`; these are browser-test artifacts, not live
recovery. None of these files was removed or modified.

Recovered complete live sample records: **0**. Retained schema probe: **1**.
Reported sample outcomes remain one failed and four completed, without retained
complete records. The first sample's exception is unavailable; no prompt defect
or deterministic processing defect has been established. The known probe cost
is $0.0006268; five-call usage and aggregate spend remain unresolved. Existing
evidence proves no sample output-token bound, so it does not support the requested
conservative cost upper bound. Failure of task-cap enforcement is established;
exceeding the $83 global ceiling is not established.

**Paid execution remains blocked.** Durable runner implementation, offline fault
coverage, full locked checks, provider usage reconciliation where available, and
five real persisted accepted outputs remain outstanding. This inspection is not
unpaid readiness or completed acceptance. No additional cost claim is made.

## Offline implementation
Durable runner and mocked fault tests now implemented in `apps/triage/acceptance.py`
and `tests/test_acceptance.py`. Results survive export failure; uncertain attempts
block resumption. Live execution remains blocked pending historical reconciliation
and a defensibly bounded injected adapter. CLI provides dry-run only; no live
acceptance completion is claimed.

### Bounded adapter partial checkpoint
SDK request now carries max_output_tokens (default 4096); SDK retries remain zero
and timeout explicit. Adapter binds exact config and requires an input-bound proof
callback covering instructions/schema/message framing. No such proven tokenizer
implementation is supplied yet: paid use remains blocked. Provider usage is journaled
before subsequent result validation; errors retain provider exception usage and the
original reservation. Offline checks: 86 passed, Ruff clean, Django clean, dry-run
pending=5, using /tmp environment/cache. No live inference or credential reads.
Surviving evidence still does not establish historical input bound and original
output maximum: subtotal $0.0006268 plus five unknown, total actual spend unknown.
No historical zero or speculative reservation claimed.
