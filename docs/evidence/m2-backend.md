# M2 backend checkpoint

Base: f3081346ab56e59c9ff494f18e417e3df6915d05. No live model calls.

Environment: locked uv environment reused at /tmp/arcvault-pr3-venv, cache /tmp/arcvault-uv. Tests used DJANGO_SECRET_KEY=test and DATABASE_URL=sqlite:////tmp/arc-backend.sqlite.

Commands and results:
- `uv run --locked python manage.py makemigrations triage`: generated initial migration (after supplying required environment).
- `/tmp/arcvault-pr3-venv/bin/pytest -q`: 64 passed. Four staticfiles-directory warnings.
- `python manage.py check`: no issues.
- `ruff check .`: passed after generated-migration RUF012 exemption.

New tests cover authentication, session CSRF rejection, invalid bearer precedence, payload validation, exact replay/conflict, incomplete export, mocked successful persistence/export fidelity, completed duplicate suppression, three-attempt transient exhaustion, and visible dispatch failure. Pipeline is called directly with an injected mock provider. Publication is mocked; this is neither real queue nor live model evidence.

Provider PR4 was inspected read-only. Lazy get_provider imports its adapter only when work runs; missing provider/config safely fails processing. Adapter owns SDK max_retries=0. Accepted output is revalidated before deterministic policy. Retry attempt usage is preserved when available; cost remains explicitly unknown.

Pending: real Postgres concurrency and Redis/Celery acceptance, worker crash recovery/operator republication, broader boundary tests, successful session-CSRF test, exact five-input sample loader/export command, frontend, provider merge and live five-output acceptance. No automatic recovery of abandoned processing claims is claimed. Early retry delivery is ignored; broker countdown is relied on. M2 integration gate remains open.
