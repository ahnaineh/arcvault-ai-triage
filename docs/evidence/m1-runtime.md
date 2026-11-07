# M1 runtime evidence — 2026-11-07

Scope: runtime only; live model/schema, policy and intake remain pending.

Primary version source: https://www.djangoproject.com/download/ lists 6.1.3.
Python 3.14.4 is available locally; installation of Django 6.1.3 on it succeeded.
Package metadata and uv.lock record resolved compatibility and exact versions.
Images use explicit version tags (not immutable digests).

Executed:
- UV_CACHE_DIR=/tmp/arcvault-uv uv lock: resolved 49 packages.
- UV_CACHE_DIR=/tmp/arcvault-uv uv sync --locked: installed 45 packages.
- DJANGO_SECRET_KEY=test DATABASE_URL=sqlite:///:memory: .venv/bin/python manage.py check: no issues.
- Same environment, manage.py makemigrations --check --dry-run: no changes.
- .venv/bin/ruff check . --fix: passed after mechanical fixes.
- Same environment, .venv/bin/pytest -q: 2 passed, 2 warnings (staticfiles absent locally before collectstatic).
- Docker requires escalation on this host. Compose integration outcome recorded below.

Unit checks mock Redis; they do not prove real Redis connectivity.
CI expands naturally as other delegates add tests; no live model calls are in CI.

## Independent integration acceptance
Reviewed runtime head: ae0d038d16f0527f8f9e146260a7040c11264c6f.
Integrated main c7fb3d5, preserving PR2 schema, policy and completed tracker entries.
2026-11-07: root had 795 MB available; /tmp is tmpfs with 6.7 GB available.
Used native isolated /tmp/arcvault-pr3-venv, UV_CACHE_DIR=/tmp/arcvault-review-uv:
- uv sync --locked: 45 packages installed, Python 3.14.4, Django 6.1.3,
  Ruff 0.17.4, pytest 9.2.0.
- uv run --locked ruff check .: passed after mechanical PR2 lint fixes.
  ValueError retained for Pydantic validation with targeted TRY004 annotation.
- DJANGO_SECRET_KEY=test DATABASE_URL=sqlite:///:memory: python manage.py check: passed.
- Same environment: python manage.py makemigrations --check --dry-run: no changes.
- Same environment: pytest -q: 60 passed, two missing-staticfiles warnings.
Existing worker: docker exec arcvault-review-sol-3-worker-1 celery -A config.celery:app inspect ping: one node pong.
Prior independent review reported matching image hashes and healthy DB/Redis HTTP200;
this run could not reproduce localhost:18373 health (curl exit 7).
Fresh Compose startup and clean image build remain pending due to constrained root disk;
no images downloaded, existing stack changed, or unrelated resources deleted.
No live model calls. This is not full clean-checkout acceptance.
M2 entry points: config/settings.py, config/urls.py (/health/), config/celery.py,
apps/triage/schemas.py and apps/triage/policy.py; compose.yaml defines service topology.
