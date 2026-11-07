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


## PR7 integration checkpoint
Reviewed head: df5fa91a28fbca43601cfca1712aceeda93846dc. Parent-supplied independent review: no blockers; original Downloads DOCX five strings matched; shared acceptance service/stable principal keys; SQLite five first dispatches, zero repeat dispatches, conflict without extra dispatch; ordered export completion/result/source/message guards; 74 locked tests and Ruff/Django/no migration drift passed. This proof is supplied review evidence, not independently repeated DOCX or historical spend verification.

Fresh implementation verification: 78 locked tests pass, Ruff passes, Django check passes, no migration drift. Added actual task pipeline with mocked provider and full persisted record export equality in sample order; missing accepted result and mismatched source/message fail with zero JSON written, including after earlier valid samples. README exports to temporary file and renames only on success. No OpenAI calls. Live provider, real queue and PostgreSQL acceptance remain pending; historical spend is not independently verified.
