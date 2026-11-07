PR9 offline completion proof, 2026-11-07

Expected base f1b5197824eb6a4fc668bb27832163a4c11cd4e5 fetched and verified.
Locked suite: 107 passed (14 added command/metadata cases), six missing-staticfiles
warnings. Ruff clean; Django check clean; no migration changes; fresh SQLite
migration applied. README dry-run: {"dry_run": true, "pending": 5}.

Mocked SDK envelopes cover command arguments/config, dry-run without SDK creation,
five full ordered valid outputs, journal/export, resume without calls, rejected
history/config/budget, HTTP failure, refusal, incomplete, semantic invalidity,
oversized output, response write failure and atomic export recovery. Content is
persisted before validation. Reservations survive uncertain attempts. Metadata
limits and allowlist tested. SDK retries zero; Terra cap explicit.

Actual historical cost unknown: dashboard report six requests, rounded 5.6K input,
zero displayed. Accepted 6.22326144 planning reservation against 83 remains
conditional on documented assumptions, not measured cost. No live inference or
real credentials used. Account/schema/queue acceptance remains next task.
