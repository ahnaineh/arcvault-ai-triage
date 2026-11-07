PR1 offline completion
======================

All 50 actual messages and category, priority, entity, signal, routing and summary
annotations were inspected. Per-case verdicts are in evals/review.jsonl. Test cases
were inspected only for label quality; no prompt was changed. The five assessment
messages and sources match samples/inputs.json verbatim.

Family IDs do not cross splits, but semantic independence is limited: outages,
restoration, configuration questions, conflicting intents and billing boundaries
recur across splits with different wording. The locked mobile cases resemble the
development outage contrast, and weekly billing resembles the threshold family.
This is a small synthetic contrast suite, not evidence of distributional breadth.
Multi-intent primary-category alternatives are recorded in the audit; exact routing
still uses the declared primary-category convention.

Canonical export adapter: inspected PR9 head
01d8828059f3dd8bf207a121f515737f4d7c2527 apps/triage/export.py and acceptance.py.
Match requests by exact source/message because application UUIDs are not case IDs;
ambiguous/unmatched requests fail explicitly. Preserve analysis, routing, provenance,
processing and application review. Application review never grants manual summary
acceptance. Missing output becomes an operational failure; omitted cases retain
the scorer's full denominator. PR9 exports only completed records; failed attempts
are journaled separately and must be supplied as request/error records if scored.

File commands (no model calls):

    python3 -m evals.export_adapter assessment_outputs.json predictions.json
    python3 -m evals.score score predictions.json --split assessment > report.json

Verification with UV_CACHE_DIR=/tmp/arcvault-uv,
UV_PROJECT_ENVIRONMENT=/tmp/arcvault-eval-complete-venv,
DJANGO_SECRET_KEY=offline-test-secret and
DATABASE_URL=sqlite:////tmp/arcvault-eval.sqlite3:

- uv run --locked pytest tests/test_eval.py tests/test_export_adapter.py -q: 11 passed before added confidence regression.
- python3 -m evals.score validate: 50 validated.
- uv run --locked pytest -q: 105 passed, six missing-staticfiles warnings.
- uv run --locked ruff check .: passed.

Refreshed all seven inline comments: original four remain covered; three new
comments addressed by metadata projection, removal of injected mandatory facts,
and confidence-aware routing/counts. No replies posted or threads resolved.
Current main 2b42ec3039df34b2a6d95abddac7fe1d33d4043a integrated; latest main
WORK_PLAN preserved. Fixture results are regression checks, not measured model
metrics. Live benchmark and independent manual review of generated summaries remain.
