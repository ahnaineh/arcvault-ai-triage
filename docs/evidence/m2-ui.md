# M2 UI checkpoint

Implemented Django session login, POST-only CSRF logout, authenticated inbox and persisted Human Review filter, original-message/detail/evidence/attempt views, completed JSON export links, and JSON webhook tester. All customer/model text uses template autoescaping or textContent. No bearer token is exposed. Single-organization authenticated access matches the existing API contract.

Tester freezes its payload/key after submission, reuses that key on uncertain retries, creates a new key only for a new intentional submission, polls at one-second intervals for at most 60 checks, aborts network requests on teardown, stops on terminal states, and offers resume after network interruption/visibility pause/window expiry. Assets are local custom CSS and vanilla JS; no CDN or HTMX dependency is needed.

Design: white #ffffff surfaces on blue-gray #edf3f8, ink #18324b, navigation #183f68, action #205a92, focus #a34d00. Trebuchet/system sans, left alignment, a quiet inbox table and original-message/analysis split collapsing on mobile. Visible status words accompany every state.

Commands (2026-11-07):

```sh
UV_CACHE_DIR=/tmp/arcvault-uv UV_PROJECT_ENVIRONMENT=/tmp/arcvault-ui-venv uv sync --locked
DJANGO_SECRET_KEY=test DATABASE_URL=sqlite:///:memory: /tmp/arcvault-ui-venv/bin/pytest -q
/tmp/arcvault-ui-venv/bin/ruff check .
DJANGO_SECRET_KEY=test DATABASE_URL=sqlite:///:memory: /tmp/arcvault-ui-venv/bin/python manage.py check
DJANGO_SECRET_KEY=test DATABASE_URL=sqlite:///:memory: /tmp/arcvault-ui-venv/bin/python manage.py makemigrations --check --dry-run
```

Results: 72 tests passed; Ruff clean; Django zero issues; no migration changes. Five warnings report absent collected staticfiles in tests. UI integration test uses real intake and processing with mocked provider, proves successful session+CSRF submission, missing-CSRF rejection, incomplete/completed export, login redirects, POST logout, persisted review filtering and escaped customer/model text. This is offline fixture verification, not live inference or Redis/PostgreSQL acceptance.

Screenshot attempt: existing google-chrome headless against actual Django-rendered fixture HTML exited 133 with crashpad `setsockopt: Operation not permitted (1)`. No screenshots produced; no visual/browser interaction acceptance claimed. No browser installation attempted. JS polling remains in need of browser interaction validation.

Remaining: actual queued Redis/Celery/PostgreSQL integration, live model outputs, clean container build, benchmark, screenshots/recording. Backend exposes no manual retry endpoint, so UI explicitly reports that limitation and offers no fake retry action. Review is read-only. No pipeline/policy/provider changes.

## PR 6 lifecycle correction and re-verification
Reviewed actual branch pr-6 at c61e53913192c86eae039413f352361ff2dd498e (uv.lock, config and apps application packages present). The previous independent reviewer stayed on dd2c7e4 and skipped execution; that review does not verify this UI.

Fixed permanent stopped flag after pagehide: pageshow restores intentional Resume, pagehide aborts fetch and cancels the polling wait, generation guards discard stale polling work, and a single-flight guard prevents duplicate submissions/pollers. Payload and idempotency key remain unchanged after uncertain delivery.

Executed on the corrected branch:
- UV_CACHE_DIR=/tmp/arcvault-uv UV_PROJECT_ENVIRONMENT=/tmp/arcvault-ui-venv uv sync --locked: passed.
- node tests/js/tester.cjs: passed executable DOM/fetch harness; Back lifecycle recovery, uncertain delivery key retention, duplicate Resume suppression and known-request status-only resume.
- DJANGO_SECRET_KEY=test DATABASE_URL=sqlite:///:memory: /tmp/arcvault-ui-venv/bin/pytest -q: 72 passed, five missing collected-static warnings. Independently reran real session/client CSRF POST 202, mocked provider processing, detail/export, missing CSRF and hostile-content escaping.
- /tmp/arcvault-ui-venv/bin/ruff check .: passed.
- Same environment python manage.py check: zero issues; makemigrations --check --dry-run: no changes.

Browser probe: sandbox Chrome exited 133, crashpad setsockopt Operation not permitted (1). Escalated installed Chrome --headless --disable-gpu --dump-dom about:blank succeeded (GPU vaInitialize warning). Browser is therefore available outside sandbox, but interactive fixture-server acceptance has NOT been completed. No screenshots or browser POST/progress/error/Back/desktop/mobile acceptance claimed. This remains a required gate before merge. No live model calls. Existing live/provider/queue/PostgreSQL/container/benchmark gates remain pending.

Real Chrome follow-up: see [execution and limitations](pr6-browser/execution.md). Six actual browser screenshots now persisted. Partial browser acceptance completed; remaining lifecycle/fault assertions still gate merge.
