# Submission index

- [Architecture (short write-up)](ARCHITECTURE.md)
- [Exact final prompt](../../prompts/triage_v4.txt) and [contract](../prompts.md)
- [Five actual final JSON records](../evidence/final-v4/assessment_outputs.json), in assessment order: login, bulk export, invoice, Okta, dashboard outage.
- [Final metrics and provenance](../evidence/final-v4/README.md)
- [Synthetic queue acceptance](../evidence/infrastructure-acceptance.md)
- [Recording script and email draft](HANDOFF.md)

Prompt rationale: triage_v4 asks Terra for all model-owned fields in one strict-schema call. It separates instructions from customer text and defines outage, priority and exact-evidence rules. Python keeps routing and arithmetic. The shorter prompt reduces instruction bulk but did not improve overall scores over V3. Exact excerpts help check evidence; they cannot prove meaning. The final settings are reasoning none and a 4096-token output cap. With more time I would review summaries and entity specificity first. Tuning is closed.

AI-assisted development lessons: AI accelerated implementation and review, but substantive PR feedback was initially missed; review threads must be inspected rather than treating green tests as complete acceptance. Early execution evidence was lost, so later claims must rely on retained artifacts rather than reconstructing a success story. Durable accounting was corrected to carry reservations across phases and preserve uncertain failed calls. The conservative accounted total is $39.99125174 of $83; actual billing remains unknown. These are observed limitations and corrections, not claims that AI removed the need for engineering judgment.

## Startup and demo

From repository root, copy `.env.example` to `.env` only if absent, replace the secret/password and securely supply OPENAI_API_KEY when a newly authorized real-model run is intended. Compose defaults to Terra/V4. Run:

```sh
docker compose -p arcvault-submission config --quiet
docker compose -p arcvault-submission up --build -d
docker compose -p arcvault-submission exec web python manage.py createsuperuser
curl --fail http://localhost:8000/health/
docker compose -p arcvault-submission exec worker celery -A config.celery:app inspect ping
```

Port 8000 must be free. Visit `/login/`, `/tester/` and `/`. Loading samples publishes inference work: do not run it under the current no-new-inference instruction. For a future authorized demo use `docker compose -p arcvault-submission exec web python manage.py load_samples --principal assessment`; after all five complete, export with `docker compose -p arcvault-submission exec -T web python manage.py export_samples --principal assessment > /tmp/assessment-outputs.json.tmp` and move the temporary file only on success. Existing sample keys replay without republishing. Stop only this project with `docker compose -p arcvault-submission down` (no volume deletion).

Clean image build remains unverified: root is 98% full with about 2 GB available. Docker data root is /var/lib/docker; cached images belong to existing ArcVault and RPiDoor stacks. No prune, deletion or downloads were performed. Configuration/command inspection does not establish a clean build. See WORK_PLAN for latest isolated startup result.
