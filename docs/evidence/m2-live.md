# Sample command checkpoint — 2026-11-07 UTC

Latest main fetched explicitly; switching main was refused because another worktree
owns it. Created feat/m2-samples-live from origin/main in the prepared checkout.
Original five source/message strings extracted verbatim from supplied attachment;
only sample inputs are committed, not the assessment document.

74 pytest tests passed using existing /tmp/arcvault-pr3-venv and an isolated SQLite
test database. Ruff, Django check, makemigrations --check --dry-run and both Node
harnesses passed. Staticfiles warnings are existing test configuration warnings.
Tests cover repeated load, principal isolation, incomplete export emitting no JSON,
source fidelity and exact DB record export ordering. These are offline tests.

No OPENAI_API_KEY in this process environment. Secure request_secret file request
timed out. No inference requests made: task spend $0; no unknown-cost attempts.
Prior provider.md records zero earlier inference spend; no account-wide balance
has been verified. Task allowance remains $3, cumulative authorized ceiling $83.
No real output file generated and no live schema/quality acceptance claimed.

Docker socket access failed with permission denied. Root has 3 GB available (96%
used); no pulls, builds, pruning or other stack mutations performed.

Official model page fetched 2026-11-07:
https://developers.openai.com/api/docs/models/gpt-4.1-mini
Model selection, exact strict-schema compatibility and pricing verification remain
pending credential/runtime continuation; adapter and prompt remain unchanged.

Remaining: obtain secure credential; verify current official pricing/schema support;
run one sample as schema smoke, record actual usage/latency/model and hashes of
prompt/schema/policy/code, then remaining four within budget. Use test-owned
Postgres/Redis and worker for queued acceptance. Export only persisted completed
records; manually review invoice difference 260 and outage escalation against source.
No confidence calibration or production accuracy is asserted.
