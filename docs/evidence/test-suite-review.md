# Test suite review — 2026-11-07

Scope: bounded test cleanup based on PR14's published head
`0d457a2fff8690d91a477998c0a1c5152172c042`, independently verified against GitHub.
Branch: `t3/test-suite-cleanup`; PR targets `t3/benchmark-prompt-refinement` so its
review diff contains only this cleanup. No production code, prompts, config,
benchmark commands, prompt-configuration tests, runtime evidence or WORK_PLAN edits.
No paid calls, secret reads, Docker operations or delegated agents.

## Findings and changes

Three acceptance-command tests executed the same SDK → runner → export seam:
`test_execute_order_artifacts_resume`,
`test_command_assessment_billing_and_outage_regression` and
`test_command_full_export_matches_canonical_builder`. The last computed expected
results with the same production `build_record` used by the command, so a shared
builder defect could pass. Consolidated into
`test_command_assessment_export_and_resume`, using independent literal outcomes.
Removed the now single-use `execute_assessment` helper and repeated five-response
execution. Existing `command`, `valid_response` and `assessment_payloads` interfaces
remain available to other tests.

The two raw-response write-failure tests duplicated the same `Runner.append` fault
injection. One parametrized test now exercises success responses and HTTP errors,
with separate literal full-usage/partial-usage expectations. Both assert retained
reservation, missing raw event, failed event, and sensitive-text exclusion.

## Behavior-to-test coverage

| Behavior | Before | After |
| --- | --- | --- |
| Five samples in order; original message/source and extracted analysis | Three overlapping command executions | One five-category command execution with ordered exact input/payload comparisons |
| All category destinations; billing $260, exact assumptions, outage review/reasons | Literal billing/outage assertions plus production-derived full record | Literal destinations and reason lists for all five categories, literal billing difference and assumptions |
| Complete export shape, provenance, processing and review defaults | Full-record equality against production builder | Explicit key sets, versions, direct file-byte SHA-256 checks, request/attempt identity links, literal usage/cost/review defaults |
| Completed replay avoids extra inference; SDK owns no retry | Separate generic success command test | Same checks in consolidated assessment command test |
| Disk failure after successful SDK response or HTTP error | Two near-identical fault-injection tests | Two named parameter cases, distinct usage outcomes and common durable journal assertions |
| Auth, CSRF, idempotency, task redelivery, dispatch failure and retry exhaustion | Backend/UI tests | Unchanged |
| Money precision, exact evidence, null invoice basis and conflict rejection | Policy and saved-invoice regressions | Unchanged |
| Runner crash, unresolved reservation, atomic export recovery, serial budget and reconciliation | Runner, command and accounting layers | Unchanged; retained because the seams/failure modes differ |
| Exact prompt identity, changed artifacts, completed/partial replay, dry-run and benchmark identity | Prompt configuration and command regressions | Unchanged |

The saved invoice and accounting evidence fixtures remain because they reproduce
specific persisted payload shapes, rather than merely duplicating synthetic data.
No broad fixture extraction or test-style rewrite was justified for this cleanup.

## Verification

All uv invocations used `UV_CACHE_DIR=/tmp/arcvault-uv` and
`UV_PROJECT_ENVIRONMENT=/tmp/arcvault-test-cleanup-venv`; Python tests used
`DJANGO_SECRET_KEY=synthetic-test-cleanup` and
`DATABASE_URL=sqlite:////tmp/arcvault-test-cleanup.sqlite3`.

- `uv sync --locked`: passed with Python 3.14.4.
- Focused `uv run --locked python3 -m pytest tests/test_acceptance_command.py tests/test_acceptance.py tests/test_prompt_configuration.py -q`: **35 passed**.
- Temporary `/tmp` pytest fault-injection plugin changed exported `estimated_cost`
  from `None` to `'0'`: the consolidated test failed at its literal processing
  assertion, as intended. No mutation or plugin was added to the repository.
- Full locked suite, run once after cleanup: `uv run --locked python3 -m pytest -q`:
  **175 passed**, six existing missing-staticfiles warnings.
- `uv run --locked ruff check tests/test_acceptance_command.py`: passed.
- `uv run --locked ruff check .`: three existing findings in unchanged, protected
  evidence scripts: I001 in `docs/evidence/comparison-v3/audit_evidence.py` and
  `docs/evidence/comparison-v3/build_report.py`; BLE001 in the latter. These remain
  for the parent evidence workstream; this is not a clean repository-wide lint run.
- `git diff --check`: passed. JS files untouched, so JS harnesses were not rerun.

No new production defect was established. Offline SQLite/mocked SDK checks do not
establish PostgreSQL/Redis runtime or live provider acceptance.

Parent tracker entry (apply in the parent's checkout, not here):
`Test-suite cleanup: consolidated overlapping acceptance-command export tests into independent literal contract checks; parametrized raw-response disk failures without losing HTTP/success usage cases. Evidence: docs/evidence/test-suite-review.md. 175 locked offline tests pass; changed-file Ruff passes; repo Ruff has 3 pre-existing comparison-v3 evidence-script findings. Separate PR; no merge performed.`
