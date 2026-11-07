# PostgreSQL / Redis / Celery acceptance — 2026-11-07

Base: latest fetched main `7149968aadd0989b695897a44aced1433ab6ad3b`, including PR10 startup fix. No live inference, credentials read, evaluation data changes, image pull/build/prune, or existing-stack mutations.

## Executed proof

Initial sandbox Docker socket permission denial was retried with require_escalated; access succeeded. `df -h / /tmp`: root 98%, 2.1 GB available; tmpfs /tmp 6.2 GB available. `docker images` and `docker ps -a` inspected first. Existing review and RPiDoor stacks preserved.

Command: `ARCVAULT_INFRA_OPT_IN=yes bash tests/infrastructure/run.sh` (Docker permission required). It creates a dedicated network, PostgreSQL tmpfs container, Redis container and web/worker/client containers, using existing images only; cleanup removes only named task resources. No exposed host ports. Source bind mounted read-only at /workspace, preserving image /app/.venv. First mount at /app masked dependencies and failed with ModuleNotFoundError: django; corrected before acceptance.

Images: postgres:18.3 (`7e32e9833a6f`), redis:8.6.1 (`315270d16608`), arcvault-review-sol-3-web:latest (`75afde218681`). Python 3.14.4. Current settings and config Celery registration run in fresh web and worker processes; web uses Django runserver, not production gunicorn. Worker uses solo pool. HTTP bearer authentication uses only an explicit synthetic test token. Dedicated Redis owns its full namespace and default queue.

Provider is explicitly replaced only by tests/infrastructure/runtime.py in the test worker. All inference is synthetic; actual HTTP, Celery publication/consumption, Redis, PostgreSQL locking/uniqueness and persistence execute normally. Provider asserts connection.in_atomic_block is false.

Successful final run assertions:
- Eight concurrent identical HTTP submissions: exactly one 202 and seven 200; one request ID.
- Five additional broker deliveries: one attempt and one accepted Result.
- Authenticated HTTP status/export exactly equal the actual PostgreSQL Result record.
- Transient synthetic error: actual 10-second broker countdown retries; terminal failed after exactly three attempts, error provider_transient.
- Permanent synthetic error: failed after exactly one attempt, error provider_auth.
- Simulated apply_async publication exception: durable pending + dispatch_failed; operator service dispatch republishes and completes. This simulates publication failure, not a real Redis outage.
- Early delivery of a retrying request with a future deadline: zero attempts before deadline, broker replacement delivery completes with one attempt.
- Final DB: six requests, four completed results, two failed; eight attempts (four successful, three transient failures, one permanent failure). Dispatch errors cleared after recovery. Test-owned resources removed by EXIT trap.

## Concrete fix

Previously process returned on early delivery without publishing replacement work. A sole early delivery could leave retrying indefinitely. It now registers post-commit dispatch with the remaining countdown rounded upward. Integration explicitly exercises this path. This is focused retry behavior, not worker-crash recovery/outbox architecture. Source change requires review.

## Other validation and remaining gates

`UV_CACHE_DIR=/tmp/arcvault-uv UV_PROJECT_ENVIRONMENT=/tmp/arcvault-infra-verify-venv DJANGO_SECRET_KEY=<synthetic> DATABASE_URL=sqlite:////tmp/arcvault-infra-unit.sqlite uv run pytest -q`: 144 passed, six existing missing-staticfiles warnings. Executed after source fix. Focused Ruff and git diff --check pass.

Clean image build/start remains pending: reused existing dependency image with latest code mounted. Production gunicorn/static asset startup, live provider/schema/account access, session-authenticated real HTTP path, and real broker-outage injection are not established by this run. Existing unit session/CSRF checks are separate evidence. No automatic worker-crash recovery claim. The harness requires its task container names to be unused; run it only with explicit opt-in and no concurrent harness invocation.
