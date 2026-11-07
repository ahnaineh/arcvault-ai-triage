# Submission index

- [Architecture (short write-up)](ARCHITECTURE.md)
- [Exact final prompt](../../prompts/triage_v4.txt) and [contract](../prompts.md)
- [Recorded live demo](demo/README.md)
- [Five JSON records shown in the demo](demo/narrated-five-outputs.json), in assessment order: login, bulk export, invoice, Okta, dashboard outage.
- [Benchmark results and model choice](BENCHMARKS.md)
- [Synthetic queue acceptance](../evidence/infrastructure-acceptance.md)

Prompt rationale: triage_v4 asks Terra for all model-owned fields in one strict-schema call. It separates instructions from customer text and defines outage, priority and exact-evidence rules. Python keeps routing and arithmetic. The shorter prompt reduces instruction bulk but did not improve overall scores over V3. Exact excerpts help check evidence; they cannot prove meaning. The final settings are reasoning none and a 4096-token output cap. With more time I would review summaries and entity specificity first. Tuning is closed.

AI lessons: passing tests did not catch missed PR feedback; I added an explicit comment audit. An early run lost its output records; later runs save responses and usage before validation. Failed calls retain budget reservations rather than being counted as free. These corrections are documented in the linked evidence.

## Startup and demo

From repository root, copy `.env.example` to `.env` only if absent, replace the secret/password and supply OPENAI_API_KEY securely for live inference. Compose defaults to Terra/V4. Run:

```sh
docker compose -p arcvault-submission config --quiet
docker compose -p arcvault-submission up --build -d
docker compose -p arcvault-submission exec web python manage.py create_demo_user
curl --fail http://localhost:8000/health/
docker compose -p arcvault-submission exec worker celery -A config.celery:app inspect ping
```

Local demo login: **admin / admin**. The setup command requires `DJANGO_DEBUG=true` and creates a regular application user.

Port 8000 must be free. Visit `/login/`, `/tester/` and `/`. Loading samples makes model calls. For a live demo use `docker compose -p arcvault-submission exec web python manage.py load_samples --principal assessment`; after all five complete, export with `docker compose -p arcvault-submission exec -T web python manage.py export_samples --principal assessment > /tmp/assessment-outputs.json.tmp` and move the temporary file only on success. Existing sample keys replay without republishing. Stop only this project with `docker compose -p arcvault-submission down` (no volume deletion).

A fresh application image build and the combined live-model queue demo passed. See [recording and verification](demo/README.md). Base-image layers were cached.
