# Offline policy 1.1 review

Reviewed PR12 head 88303f7f4c3b544647ef2b0d982bb7b71bbbe376 and fetched main
7149968aadd0989b695897a44aced1433ab6ad3b. This is an application fix on PR12,
which retains its original evidence dependency. No inference or key access.

Cause: extraction correctly retained absent billed period AND both component fields
as null. Policy 1.0 required populated periods/components before applying the
ASSESSMENT_PLAN.md synthetic-domain convention (lines 238, 304). This is a policy
coverage gap, not evidence that extraction should invent missing facts.

Policy 1.1 accepts a conservative complete-statement grammar for a direct invoice
charge versus monthly contract rate. It assumes one month and equal components
separately; extracted nulls remain null. Additional clauses, explicit incompatible
periods/components/currencies or missing amounts remain unresolved. The grammar
intentionally rejects other wording pending a reviewed rule extension.

Manual review of all five original analyses and raw responses:
1. Login: Bug Report, Medium, Engineering. 403, account URL and both time
   expressions faithful; two-sentence summary attributes timing to customer.
2. Audit export: Feature Request, Low, Product. Audit logs/monthly savings
   faithfully represented; no urgency invented.
3. Invoice: Billing Issue, Low, Billing after offline derivation; apparent 260
   under declared assumptions. Invoice entity and monthly rate faithful. Low
   differs from plan's illustrative Medium priority; no explicit urgency supports
   forcing Medium, so retained as an extraction judgment, not silently corrected.
4. Okta: Technical Question, Low, Technical Support. SSO/Okta entities and
   two-sentence evaluation summary faithful.
5. Dashboard: Incident/Outage, High, Human Review (active_outage), standard
   Engineering. Multiple users and 2pm EST faithfully retained; provider fault
   attributed to customer, not independently verified.

All five contain required fields, valid labels, exact evidence excerpts and two
faithful summary sentences. Unknown customer urgency retained for all five.
scripts/reprocess_invoice_evidence.py verifies raw Analysis equality, validates
against original messages, and uses the canonical builder. Versioned output
assessment_outputs.policy-1.1.json records source hash and code hashes. Original
records/raw journal remain unchanged. Original completion timestamps describe the
original model completion; offline_derivation explicitly identifies reprocessing.

Five original Terra calls, zero retries: 4738 input / 1026 output tokens.
0.069047 is a conservative usage estimate, not actual billing.
75.92876544 is retained reservations, not spend. Actual billed cost unknown.
No queue/Postgres, fresh model run, deployment or paid acceptance is claimed.

Validation: full offline SQLite suite 155 passed (six existing missing-staticfiles
warnings); Ruff clean; Django system check clean; git diff --check clean.
All uv calls used /tmp/arcvault-uv and /tmp/arcvault-invoice-live-fix-venv,
explicit SQLite and offline-test-key. No Docker operations.
