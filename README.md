# ArcVault

AI-powered intake and triage for synthetic B2B support requests. A webhook saves each message, a worker calls the model, and Python applies routing and escalation rules. The UI shows the result and its supporting evidence.

**[Start with the submission package](docs/submission/README.md)** — demo video, five JSON outputs, architecture, exact prompt and evaluation results.

## Run locally

Requirements: Docker with Compose, port 8000 available, and an OpenAI API key for new analyses.

```sh
cp .env.example .env
# In .env, set DJANGO_SECRET_KEY, POSTGRES_PASSWORD and OPENAI_API_KEY.
docker compose up --build -d
docker compose exec web python manage.py create_demo_user
```

Open **http://localhost:8000/login/** and sign in with **admin / admin**. This is a regular demo user, not a Django administrator. The setup command requires `DJANGO_DEBUG=true` and leaves existing accounts with different credentials unchanged.

Use **Test a request** to submit a message. The inbox shows its status and destination; the detail page shows category, priority, confidence, urgency, core issue, summary, entities and escalation status. **Export JSON** returns the saved record. Human Review is a read-only queue in this assessment.

Compose runs migrations before starting the application. PostgreSQL data persists in a named volume. To stop this local stack without deleting its data:

```sh
docker compose down
```

## Process the five assessment inputs

These commands make model calls. Run the export after all five requests complete.

```sh
docker compose exec web python manage.py load_samples --principal assessment
docker compose exec -T web python manage.py export_samples --principal assessment > /tmp/assessment-outputs.json.tmp &&
  mv /tmp/assessment-outputs.json.tmp /tmp/assessment-outputs.json
```

Repeated loading uses stable idempotency keys and does not republish existing requests.

## Design and verification

Python 3.14.4, Django 6.1.3, PostgreSQL, Celery/Redis, server-rendered templates, OpenAI Responses API and Pydantic. Dependencies are pinned in `uv.lock`. The application uses `gpt-6.1-terra` with `triage_v4`, one structured request per attempt, and bounded retries for transient failures.

- [Architecture and tradeoffs](docs/submission/ARCHITECTURE.md)
- [API and data contracts](docs/CONTRACTS.md)
- [Final prompt and benchmark](docs/evidence/final-v4/README.md)
- [Live demo evidence](docs/submission/demo/README.md)
- [UI requirements and verification](docs/evidence/ui-redesign.md)
- [Progress and historical evidence](WORK_PLAN.md)

The benchmark uses 50 reused synthetic cases, not a fresh holdout. It is useful comparison evidence, not a production accuracy claim. Known limits include worker-crash recovery, human correction actions and independent review of all generated summaries.

Local checks:

```sh
uv sync --locked
export DJANGO_SECRET_KEY=local-check-only
export DATABASE_URL=sqlite:///:memory:
uv run pytest
uv run ruff check .
uv run python manage.py check
```

Keep API keys in the local `.env` file. It is excluded from Git. For deployment, use individual credentials, disable debug mode and configure HTTPS.
