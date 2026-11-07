# ArcVault

ArcVault turns a customer message into a classified, enriched support request. It saves the result, assigns a team, and sends uncertain or high-risk cases to Human Review.

**[View the assessment submission](docs/submission/README.md)** for the demo, five JSON outputs, architecture, and prompt.

## Run locally

You need Docker Compose, port 8000, and an OpenAI API key to process new messages.

```sh
cp .env.example .env
# Set DJANGO_SECRET_KEY, POSTGRES_PASSWORD and OPENAI_API_KEY in .env.
docker compose up --build -d
docker compose exec web python manage.py create_demo_user
```

Open **http://localhost:8000/login/** and sign in with **admin / admin**. The demo account requires `DJANGO_DEBUG=true`, which is set in `.env.example`. It is a regular application user. The command leaves conflicting existing accounts unchanged.

Select **Test a request**, submit a message, and open its result. The detail page shows the analysis, destination, supporting excerpts, and JSON export. **Human Review** lists escalated requests; approval and correction actions are not implemented.

## Process the assessment inputs

This command submits the five supplied messages and makes model calls:

```sh
docker compose exec web python manage.py load_samples --principal assessment
```

Wait until all five requests show **Completed** in the inbox, then export:

```sh
docker compose exec -T web python manage.py export_samples --principal assessment > /tmp/assessment-outputs.json.tmp &&
  mv /tmp/assessment-outputs.json.tmp /tmp/assessment-outputs.json
```

The export fails if any request is incomplete. Repeating `load_samples` returns the same requests without starting new analyses.

Compose applies database migrations at startup. PostgreSQL keeps data in a named volume. Stop the application with `docker compose down`; this preserves the data.

## Development

Python 3.14.4, Django 6.1.3, PostgreSQL, Celery, Redis, and the OpenAI Responses API. Dependencies are pinned in `uv.lock`.

```sh
uv sync --locked
export DJANGO_SECRET_KEY=local-check-only
export DATABASE_URL=sqlite:///:memory:
uv run pytest
uv run ruff check .
uv run python manage.py check
```

[API and data reference](docs/CONTRACTS.md) · [Evaluation](docs/submission/BENCHMARKS.md) · [Verification evidence](docs/evidence/README.md)

Keep secrets in `.env`, which Git ignores. A deployed instance needs individual credentials, HTTPS, and debug mode disabled.
