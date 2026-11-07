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
