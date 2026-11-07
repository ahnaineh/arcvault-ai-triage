# Verification evidence

The [submission package](../submission/README.md) contains the reviewer-facing deliverables. This directory keeps detailed run records for reproducibility. Each record describes the code and environment used at the time.

| Evidence | What it establishes |
| --- | --- |
| [Final model run](final-v4/README.md) | Real responses and scores for 50 synthetic cases |
| [Model comparison](comparison-v3/README.md) | Terra and Luna results under the recorded configurations |
| [Infrastructure tests](infrastructure-acceptance.md) | HTTP, PostgreSQL, Redis, and Celery behavior with synthetic inference |
| [Demo checks](final-demo-checks.md) | Recorded live workflow, JSON export, and media checks |
| [Interface checks](ui-redesign.md) | Desktop, mobile, keyboard, and displayed-field verification |

Other files retain earlier implementation and experiment records. They are not additional submission requirements.
