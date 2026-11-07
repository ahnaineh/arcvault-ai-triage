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
