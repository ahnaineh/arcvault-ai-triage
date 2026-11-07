# Recorded live demo

[Watch the 2:44 demo](arcvault-demo.mp4) · [Five JSON records](live-assessment-outputs.json)

The browser submitted all five original messages to the real webhook. PostgreSQL saved them, Redis/Celery processed them, and Terra V4 produced the analyses. This is a live queued run, not replayed benchmark data.

| Input | Priority | Final queue |
|---|---|---|
| Login error | High | Engineering |
| Audit export | Low | Product |
| Invoice discrepancy | Medium | Billing |
| Okta setup | Medium | Technical Support |
| Multi-user outage | High | Human Review |

The invoice shows an apparent $260 difference with explicit currency/monthly-charge assumptions. These five outcomes do not establish general model accuracy.

## Recording and recovery

The video is a captioned screen capture, with no narration. It retains the first 55 seconds of the initial recording, then joins the resumed recording. The second request encountered a browser network interruption and one transient provider failure. The worker retried once and completed the same request. No duplicate submission was made. The long interruption is cut; the captions disclose the cut. The original captures are retained privately with hashes in [manifest.json](manifest.json).

Five requests completed in six provider attempts. Five successful attempts report usage; the transient attempt has unknown usage and retains its $11.617584 reservation. The cause of the interruption is unconfirmed.

## Verification

Application commit: `b4368bbc3ab933d45137fa4195350623a57d4f18`. A fresh application image built from the Dockerfile and locked dependencies; base-image layers were cached. Startup, migrations, database/Redis health, worker ping, login and CSRF passed. See [startup log](startup.log). The database began empty.

Each completed request was backed up and exported before the next submission. The five exported source/message pairs exactly match the assessment inputs; IDs are unique and provenance names Terra/V4. Screenshots show the [final inbox](06-inbox.png) and [Human Review queue](07-human-review.png). SQL backups, credentials and sessions are excluded from this package.

## Accounting

Total conservative accounting is **$51.67980774 of $83**, including prior uncertainties and this run's transient failure reservation. Actual billing is unknown. See [manifest](manifest.json) and [serial ledger](accounting.jsonl).

Before the final three submissions, OpenAI's input-count endpoint counted the exact model/prompt/schema/message bodies: 956, 962 and 954 tokens. A 2,000-input/4,096-output bound at $11/$16.50 per million reserved $0.27 for each request's maximum three attempts. Actual successful usage matched those input counts. Earlier uncertain reservations remain unchanged.
