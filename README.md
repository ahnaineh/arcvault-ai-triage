# ArcVault — AI intake and triage

An assessment project for classifying, enriching and routing synthetic B2B customer requests with an LLM and explicit application policies.

**Status: planning baseline published; runtime and executable contracts are next. The application is not implemented yet.** Follow [WORK_PLAN.md](WORK_PLAN.md) for verified progress, remaining tasks and completion gates.

## Planned workflow

A visual tester submits to the same webhook used by external clients. Django persists the request, Celery executes one structured model call, Python applies routing and escalation rules, and PostgreSQL stores the result for review and JSON export.

The planned stack is Python, latest stable Django, Django templates/HTMX, PostgreSQL, Celery/Redis, OpenAI Responses API/Pydantic, Docker Compose, uv, pytest and Ruff. Exact compatible dependency versions will be locked during implementation.

## Project documents

- [Execution tracker](WORK_PLAN.md): current status and acceptance evidence.
- [Architecture and assessment plan](ASSESSMENT_PLAN.md): decisions, scope and rationale.
- [Implementation contracts](docs/CONTRACTS.md): webhook, model, policy, persistence and evaluation boundaries.
- [Analysis JSON schema](contracts/analysis.schema.json): model-owned response fields.
- [Controlled policy cases](tests/fixtures/policy_cases.json): expected decisions, not live model outputs or passing tests.

## Evaluation and delivery

The target is 50 reviewed synthetic messages with separate development, validation and locked final-test splits, plus independent policy and operational tests. Each dimension of the single model response is evaluated separately; integrated tests check the final destination and persisted result.

Planned submission artifacts include the five actual assessment outputs, prompt documentation, a short architecture write-up, evaluation results and a screen recording. Setup instructions and results will be added only after the corresponding commands and runs have been verified.

Customer examples are synthetic. Credentials, local environment files and the original assessment attachment are not repository artifacts.

## Runtime foundation

Python 3.14.4 and Django 6.1.3; exact transitive dependencies are in uv.lock.
This PR supplies infrastructure only; intake and model processing remain pending.

Local checks (executed):
```sh
UV_CACHE_DIR=/tmp/arcvault-uv uv sync --locked
export DJANGO_SECRET_KEY=local-check-only
export DATABASE_URL=sqlite:///:memory:
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
uv run ruff check .
uv run pytest
```

Container setup:
```sh
cp .env.example .env
# Replace the local secret and password in .env
docker compose up --build -d
curl --fail http://localhost:8000/health/
docker compose exec web python manage.py createsuperuser
docker compose exec worker celery -A config.celery:app inspect ping
docker compose down
```

Compose runs migrations before web/worker; PostgreSQL data persists in a named
volume. Health checks test database and Redis, not model access or task execution.
No OpenAI key is needed for this foundation. Never commit .env.
For deployment set DEBUG=false, configure hosts and TLS, and enable
DJANGO_SECURE_SSL_REDIRECT behind a correctly configured TLS terminator.

Acceptance limitation: locked Ruff and 60 tests pass after integration with policy.
Fresh image build and isolated Compose startup remain pending on this disk-constrained
host; existing-worker ping passes, but localhost:18373 health was not reproduced.
See docs/evidence/m1-runtime.md for commands and evidence boundaries.

Assessment sample commands (configured isolated database and Redis worker required):

```sh
python manage.py load_samples --principal assessment
python manage.py export_samples --principal assessment > /tmp/assessment-outputs.json.tmp &&
  mv /tmp/assessment-outputs.json.tmp /tmp/assessment-outputs.json
```

Loading replays stable principal-scoped keys; it never republishes existing requests.
Export emits standard persisted records in assessment order only when all five
are complete and match the supplied inputs. Check exit status before using the file.
Live provider and queued acceptance remain pending; see docs/evidence/m2-live.md.

Persistent acceptance command (dry-run by default):

```sh
uv run --locked manage.py run_acceptance --run-dir "$PWD/.runtime/acceptance" --config config/acceptance/terra.json
# OPENAI_API_KEY must already be supplied securely in the environment.
uv run --locked manage.py run_acceptance --run-dir "$PWD/.runtime/acceptance" --config config/acceptance/terra.json --execute
```

Configuration must bind Terra, official_price_source, input/output prices per million,
input_token_bound, output_token_cap, timeout, budget, project_budget, and
reconciled_history with known_cost, unknown_reservation, evidence and provenance.
History must come from explicit account reconciliation. No historical usage is inferred.

Prepared conservative configuration: `config/acceptance/terra.json` (project/task
budget $83). Use that path in the commands above. Historical model is an explicit
recorded-report assumption; reservation is not a claim of actual cost.

For reproducible offline verification, set these before the command above:

    export UV_CACHE_DIR=/tmp/arcvault-uv
    export UV_PROJECT_ENVIRONMENT=/tmp/arcvault-pr9-finish-venv
    export DATABASE_URL=sqlite:////tmp/arcvault-pr9.sqlite3
    export DJANGO_SECRET_KEY=test

Evidence allows response ID/model/status (256/256/64 characters, with truncation
flag), numeric usage totals, and output text. JSON above 1 MiB or 16 parts fails
explicitly; byte count, usage and reservation remain. Refusal text, SDK extras,
headers and exception dumps are excluded. Missing usage means unknown cost.
Disk failure may prevent evidence writes; the durable original reservation blocks
further spending. Atomic export failure preserves completed journal records.
Compose passes raw `POSTGRES_PASSWORD` separately to PostgreSQL and Django, so
URL delimiters in passwords are preserved. Django also accepts `POSTGRES_USER`,
`POSTGRES_DB`, `POSTGRES_HOST`, and `POSTGRES_PORT`. A nonempty `DATABASE_URL`
overrides these settings for local development/tests; URL passwords must be encoded.
