# ArcVault v1 contracts

Technical reference for the intake API, model response, routing policy, and saved records. For the system overview, read the [architecture](submission/ARCHITECTURE.md).

## 1. HTTP intake and tester UI

`POST /api/v1/requests/` is the only HTTP ingestion path. The visual tester sends JSON to this endpoint using `fetch`, then polls the status endpoint. There is no separate form-only processing flow.

```json
{
  "source": "Email",
  "message": "I cannot log in. The page returns 403.",
  "idempotency_key": "tester-run-001"
}
```

- Required: `source` is exactly `Email`, `Web Form`, or `Support Portal`; `message` is a nonblank string, at most 20,000 Unicode characters. Preserve its original whitespace and wording after validation. Reject unknown fields and non-string values.
- Optional: `idempotency_key` is a nonblank string of at most 128 characters. Omit it when not needed; reject null or empty values. No text-only deduplication.
- Accept only `application/json`; limit the complete body to 128 KiB.
- Browser: authenticated Django session plus CSRF validation. External clients: one configured bearer token using constant-time comparison. A supplied invalid bearer token never falls back to session authentication. Never place the token in page source, browser storage, logs, or exports.
- This is a single-organization assessment app. Authenticated reviewers and the service-token principal can access its synthetic requests. No multi-tenant isolation is claimed.
- Idempotency is scoped to authenticated principal plus key. Compare the exact validated source and message. Same key/payload returns the original request; different payload returns 409. Enforce uniqueness in the database, including concurrent submissions.

New request: HTTP 202 after durable database acceptance, with a `Location` header for the status URL:

```json
{
  "id": "application-generated-uuid",
  "status": "pending",
  "status_url": "/api/v1/requests/application-generated-uuid/",
  "replayed": false
}
```

A replay returns 200 with the current state and `replayed: true`; it does not publish new work. HTTP 202 means accepted, not that broker publication or inference succeeded. Publish after commit with bounded broker timeouts. Preserve pending state and a sanitized dispatch error when publication fails; the status response must reveal it.

Errors use `{ "error": { "code": "...", "message": "...", "fields": {} } }`. Use 400 for malformed JSON/validation, 401 for missing or invalid credentials, 403 for CSRF failure, 409 for idempotency conflict, 413 for oversized body, and 415 for unsupported media type. API authentication failures return JSON rather than login redirects. Return 503 if durable acceptance fails; do not claim acceptance without a committed request.

`GET /api/v1/requests/{id}/` returns `id`, `status`, `received_at`, `updated_at`, `attempt_count`, `next_attempt_at`, `dispatch_error`, `error`, and `result`. Timestamps are UTC ISO 8601; absent values are null. Result is present only when completed. Errors expose stable codes and safe messages, never provider exception dumps. Unknown IDs return 404. Authentication is required.

The tester generates a new idempotency key for each intentional submission and reuses it for retries of that submission. Poll approximately once per second while visible; stop on completed/failed or page teardown. Show network errors without claiming the request failed. Provide a resume action after a bounded polling window. Render all customer/model text escaped.

## 2. Model analysis

`contracts/analysis.schema.json` defines the model-owned output. One model call returns all fields. All object properties are required, additional properties are forbidden, and missing facts use null or empty arrays as specified. Application validation adds the semantic checks below; schema validity alone is insufficient.

- `category`: one of the five assessment categories.
- `priority`: Low, Medium, High under the [prompt's impact rules](../prompts/triage_v4.txt).
- `confidence`: model-reported classification confidence, 0–1; not calibrated certainty.
- `core_issue`: one sentence grounded in the request.
- `entities`: identifiers or relevant named entities, each with type, value, and an exact supporting excerpt. Do not fetch URLs.
- `urgency`: Low, Medium, High, or Unknown plus exact excerpts supporting urgency. This describes expressed urgency; priority additionally considers impact.
- `signals.active_service_outage`: true only for a reported current broad-service/multi-user availability failure; false for individual bugs, resolved/historical/hypothetical failures, or requests without outage evidence; null only when the text raises an unresolved possible outage. Evidence is mandatory for true or null. Absence of statements about other users alone does not imply uncertainty.
- `signals.insufficient_information`: true if the request cannot be safely routed from its contents.
- `signals.conflicting_intents`: true only when material competing intents prevent one safe destination; not merely because a message mentions multiple topics.
- Each signal contains `value` and `evidence`. The last two are booleans; only outage permits null. Do not add a redundant widespread-impact flag.
- `billing_comparison`: null unless a monetary discrepancy is alleged. Otherwise preserve billed/expected decimal strings, currency tokens, billing periods/components, and exact evidence. Unknown values are null; do not calculate the difference in the model.
- `summary_sentences`: two or three concise sentences, preserving customer-reported versus verified facts. No invented diagnosis, capabilities, promises, dates, or remediation. Do not pad sparse messages with invented information.

App validation: confidence finite/in bounds; evidence nonblank and verbatim substring of input; meaningful string lengths; two/three nonblank summary entries; nonnegative, finite monetary strings using decimal arithmetic. Numeric money strings use plain decimal notation without commas or currency symbols. Evidence preserves their original representation. Source occurrences do not prove semantic correctness; evaluate that separately.

The model must never generate request IDs, queues, escalation decisions, processing timestamps, version metadata, or reviewer decisions. Refusal, incomplete response, and invalid analysis are explicit processing failures, not fabricated low-confidence analyses.

## 3. Deterministic policy

Standard queues: Bug Report → Engineering; Feature Request → Product; Billing Issue → Billing; Technical Question → Technical Support; Incident/Outage → Engineering.

Apply all matching reasons; deduplicate and emit in this fixed order:

1. `low_confidence`: confidence strictly below 0.70.
2. `active_outage`: category is Incident/Outage OR outage signal is true.
3. `inconsistent_analysis`: Incident/Outage with false/null outage signal, or true outage signal with a different category. Preserve `active_outage` too.
4. `outage_scope_unresolved`: outage signal is null. Valid analysis requires relevant unresolved-outage evidence.
5. `billing_comparison_unresolved`: alleged discrepancy cannot be safely compared under the rules below.
6. `billing_overcharge`: comparable positive USD overcharge strictly greater than 500.
7. `insufficient_information`: corresponding signal is true.
8. `conflicting_intents`: corresponding signal is true.

Any reason sets `human_escalation: true` and `final_destination: Human Review`. Otherwise final destination equals standard destination. Priority and escalation are independent. Rules are deterministic, but semantic inputs remain model judgments.

Billing: normalize explicit USD/US$ and unqualified `$` to USD under a documented synthetic-domain assumption. Missing or incompatible currencies, non-USD disputes, missing amounts, and mismatched/unknown comparison basis cause unresolved review. Treat a directly compared invoice and monthly contract rate as one monthly charge unless different periods/components are mentioned. Save that assumption explicitly; it is not a verified fact. Matching explicit periods/components are comparable. Use Decimal; compute billed minus expected, never absolute value. Preserve negative values as reported undercharges without triggering the positive-overcharge rule. Do not perform FX conversion.

The policy boundary accepts validated analysis and normalized billing comparability. Unit-test monetary normalization/arithmetic independently, then policy decisions, then their composition. `tests/fixtures/policy_cases.json` supplies controlled policy cases; these are not live-model benchmark records.

## 4. Persistence and export

Processing states: pending → processing → completed / retrying / failed; retrying → processing. Failed requests require operator intervention; there is no user-facing retry action. Claim attempts atomically and commit before calling the provider. Save accepted analysis, derived result, and completion atomically. Never hold a transaction during inference. Track every attempt; cap transient automatic retries at two after the initial call. SDK retries are disabled so one layer owns the budget.

Export record sections:

- `schema_version`: `1.0`.
- `request`: ID, source, original message, received timestamp.
- `analysis`: validated model object, unchanged.
- `decision`: standard/final destinations, escalation flag/reasons, reported overcharge as a decimal string or null, comparison assumptions.
- `summary`: joined summary sentences for the receiving team.
- `provenance`: model identifier, prompt/schema/policy versions, completion timestamp, accepted attempt ID.
- `processing`: attempts, latency, usage, estimated cost and unknown-cost status. Include retry usage; missing usage is not zero.
- `review`: null. Human correction actions are not implemented.

`GET /api/v1/requests/{id}/export/` returns the completed record; return 409 when incomplete. A management command exports the five designated sample requests in source order and fails if any are incomplete. The final evidence must match the demonstrated configuration.

## 5. Evaluation and verification

The evaluation uses 50 synthetic messages: 5 assessment, 25 development, 10 validation, and 10 test. Later comparisons reuse the test cases. See [results and limitations](submission/BENCHMARKS.md).

Each case records the message, split, expected labels and entities, summary facts, signals, and policy decision. The scorer measures each output dimension separately. Summary acceptance requires a recorded review; schema validity alone does not establish faithfulness.

Policy fixtures test confidence and billing boundaries, multiple escalation reasons, and unknown comparisons. Application tests cover authentication, CSRF, duplicate submissions, invalid provider output, bounded retries, and persisted exports. [Infrastructure evidence](evidence/infrastructure-acceptance.md) identifies which paths ran through real services and which failures were simulated. Worker-crash recovery is not implemented.


## Finalized durable recovery

The runtime scanner runs every five seconds, selecting at most 100 oldest eligible
requests per pass. Under a row lock it reserves publication for ten seconds in
dispatch_reserved_until, independently of provider retry eligibility in
next_attempt_at. Publication uses countdown=10 outside the transaction. A scanner
reservation never delays a due worker claim. A crash before publication permits
another scan after reservation expiry; repeated scans and duplicate deliveries
are safe under PostgreSQL row locks. Provider transient retries retain their
ten-second eligibility delay. Expired 120-second worker leases are fenced by
owner token and lease time, including after a replacement completes. Interrupted
attempts consume the shared three-attempt budget.

Migration 0003 adds a nullable reservation field; existing rows retain their
eligibility timestamps and become dispatchable when those timestamps are due.
This is at-least-once dispatch, not exactly-once provider execution: an interrupted
provider call may incur cost without a saved result. Recovery requires a running
scanner, database and broker. Real process-kill, broker-outage and pr