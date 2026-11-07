# ArcVault architecture

## How it works

The webhook saves the request. Celery calls the model. Python routes the result. PostgreSQL stores the original message, each attempt and the final JSON record. Redis carries the queued work. The browser tester uses the same webhook and polls for completion.

An idempotency key prevents duplicate submissions for the same caller. Work is published after the database commit. The worker claims an attempt before calling the model, without keeping a database transaction open during inference. It then saves the analysis, routing decision and completion together. Exports read that saved result.

## Model and policy

One gpt-6.1-terra call uses the compact triage_v4 prompt. It returns category, priority, confidence, entities, urgency, signals and a short summary. A strict schema checks the structure. Python checks that supporting excerpts occur in the message. Neither check proves the interpretation is correct. Confidence is the model's own estimate.

Python owns routing and money arithmetic. Bugs and incidents go to Engineering, features to Product, billing to Billing and technical questions to Technical Support. Keeping these rules outside the prompt makes them explicit and testable.

Any escalation sends the result to Human Review while preserving its normal queue. Reasons include confidence below 0.70, active or unresolved outages, contradictory analysis, insufficient information, conflicting intents and billing amounts that cannot safely be compared. A comparable positive USD overcharge above $500 also triggers review. Python uses Decimal arithmetic. The invoice sample's $260 difference relies on disclosed dollar and monthly-charge assumptions. Priority alone does not trigger escalation.

## Failures and state

The pipeline retries transient provider failures at most twice after the first attempt. SDK retries are disabled so only one layer controls retries. Refusals, invalid outputs and permanent errors remain visible failures. They do not become invented low-confidence results. Failed queue publication stays visible for operator recovery.

Attempts retain usage and unknown costs. The benchmark runner reserves money before calls and carries uncertain reservations across phases. This conservative accounting is separate from actual provider billing.

Browser access requires a login and CSRF protection. External ingestion uses a bearer token. Secrets stay in environment configuration. This is a single-organization assessment app.

## Evidence and limits

Real HTTP, PostgreSQL, Redis and Celery acceptance passed with synthetic inference. The final provider benchmark separately contains real model outputs. A fresh application image build and a [recorded real-model queued demo](demo/README.md) also passed. The demo includes one transient failure and successful retry.

On 50 reused cases, declared scorer matches were category 47, priority 40, exact entities 44 and full routing 41. For the five required inputs, category, priority and routing matched 5/5; exact entity sets matched 1/5. These are comparisons with declared labels, not absolute accuracy. Independent review of all summaries remains pending. See the [benchmark tables](BENCHMARKS.md) for results and limitations.

## Production and another week

For production, I would add reliable database-to-queue publication, worker crash recovery, queue-age alerts, tenant isolation and provider billing reconciliation. I would measure concurrency limits and review thresholds before adding model calls.

Another week would first go to summary review and worker crash recovery. Audited human corrections and queue filters would follow; they are optional for this submission.
