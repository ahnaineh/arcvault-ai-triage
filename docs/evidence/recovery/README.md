# Durable request recovery (#25)

Run `docker compose up --build`; the `recovery` service starts after migration and
runs `python manage.py recover_requests --loop`, restarting unless stopped.
For a manual pass run `docker compose run --rm recovery python manage.py recover_requests`.
Inspect `docker compose logs recovery worker` and request status/attempt records.
Deploy migration before starting the new workers; stop old worker versions during
upgrade because they do not implement ownership fencing.

The database is the durable work source. Every five seconds a scanner selects at
most 100 due rows ordered by receipt. Each selected row is locked briefly and
publication is attempted outside the transaction with a ten-second broker countdown.
A separate ten-second database publication reservation throttles repeat scans;
it never advances the provider retry timestamp or prevents a due worker claiming.
Lost/failed/uncertain publication is retried once the reservation expires.
Multiple scanners and duplicate broker deliveries are
safe: workers lock the request and only pending/retrying due requests can claim.
No transaction spans provider or broker network calls. Broker operations use the
existing three-second connection/socket limits and no publication retries.

Processing has a fixed 120-second lease, no heartbeat. A late worker cannot save
success or failure after lease expiry or replacement. Recovery records an
unfinished attempt as `worker_interrupted` without inventing usage/cost, revokes
ownership, and schedules a replacement. Old processing rows have null leases and
are immediately eligible after migration. Each claim consumes one of three total
attempts, including interrupted attempts. At exhaustion the row is terminal
failed. Completed and failed rows are never revived. Provider SDK retries remain
disabled. This bounds calls per request, not exactly-once provider execution:
crashes and slow providers can cause overlapping calls, and cost after a crash
remains unknown. A slow call exceeding 120 seconds loses its result.

Recovery requires a healthy database, running scanner and eventually available
broker/workers. There is no global latency guarantee: batches are 100, scan
interval five seconds plus publication time, and overloaded queues add delay.
Scanner restart reconstructs work entirely from persisted rows. Broker loss after
successful publication is covered by scanning due pending rows again. Monitor
scanner restarts and old pending/processing requests; a permanently unavailable
database requires operator repair. Database backup/restore remains an operator
responsibility.

Offline validation uses fake providers only. `tests/test_recovery.py` covers the
commit/callback gap, broker failure and subsequent recovery, old/expired/active
leases, duplicate delivery, stale success/error, attempt exhaustion, and terminal
rows. Its PostgreSQL-only threaded test exercises real row-lock contention; the
SQLite run skips this proof. Tests use pytest-created databases, never existing
application data. PostgreSQL proof used an isolated disposable postgres:18.3
container, not the application Compose volume.

Verified in this checkout: full SQLite offline suite **294 passed, 1 skipped**
(the skip is PostgreSQL concurrency); isolated PostgreSQL recovery suite **12
passed**. Ruff, Django system check, migration drift check and `git diff --check`
passed. Six SQLite warnings concern the existing absent collected-static folder.
No paid inference ran.

PR34 correction checks: SQLite 295 passed, 1 skipped; isolated tmpfs PostgreSQL
18.3 recovery/concurrency 13 passed; Ruff, Django check and migration drift pass.
Existing-row upgrade from 0002 preserved message and initialized reservation null.
Fake-clock 105-row backlog completes after repeated scans before workers.
Old success/error cannot overwrite completed replacement. No process-kill test
or paid inference performed. Test PostgreSQL container removed.
