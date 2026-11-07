# ArcVault delivery work plan

This file is the source of truth for execution status. Update it in every implementation commit that changes task status, scope, acceptance evidence, or blockers. Do not mark a task complete from generated code alone.

Design rationale: [ASSESSMENT_PLAN.md](ASSESSMENT_PLAN.md). Interface and policy specification: [docs/CONTRACTS.md](docs/CONTRACTS.md). If these documents conflict, record and resolve the decision here, then update the affected specification before dependent implementation.

## Current checkpoint

Application checkpoint: final demo and reviewer login merged in PR20 at 05d57cf. Prompt tuning is closed. Submission index: [docs/submission/README.md](docs/submission/README.md).

- Verified: fresh application image build, startup, five real queued Terra/V4 submissions, persisted exports and a narrated recording without subtitles. See [demo evidence](docs/submission/demo/README.md).
- All five completed; one transient provider failure retried successfully. No duplicate request was submitted.
- Remaining handoff: user makes repository public and verifies signed-out access, then sends submission. No email sent.
- Benchmark limitations remain: reused cases and pending independent summary review. Optional human correction/filter polish is deferred.
- Earlier checkpoints below are historical; this checkpoint supersedes stale pending claims.

## Status and evidence rules

Use `[ ]` for pending, `[-]` for active, `[x]` for verified complete, and `[!]` for blocked. Each completed milestone links to evidence or records the command and observed result. Keep at most one integration milestone active; parallel tasks may run within it with distinct file ownership.

Distinguish specification checks, mocked tests, real container integration, live model runs, and submission evidence. Never substitute one for another. Save a complete submission checkpoint before optional expansion. Publishing this repository is authorized; sending the recruiter email is not yet authorized.

## M0 — Specifications and repository

- [x] Record architecture, chosen stack, webhook-first flow, budget, and 50-case split in the assessment plan.
- [x] Define HTTP intake/status/export behavior and model/policy ownership in `docs/CONTRACTS.md`.
- [x] Draft strict model JSON schema in `contracts/analysis.schema.json`.
- [x] Define 25 controlled policy cases in `tests/fixtures/policy_cases.json`.
- [x] Verify JSON parsing, unique case IDs, and strict object required/additional-property structure. These checks do not prove provider schema compatibility or policy correctness.
- [x] Create this execution tracker and a reviewer-facing repository introduction.
- [x] Initialize Git, commit the planning artifacts, create private GitHub repository, and verify the pushed commit. `gh repo view` confirmed private visibility and `main`; `git ls-remote` matched baseline commit `2eedbbec13fdac5eb43a59bcde5ced64e3b87ca8`.

Gate: remote repository contains the intended planning artifacts and no credentials or assessment attachment.

## M1 — Runtime and executable contracts

- [x] Verify Django 6.1.3 and Python 3.14.4 installation; lock dependencies and version-tag container images. See docs/evidence/m1-runtime.md (images are not digest pinned).
- [x] Select an initial OpenAI model using current documented availability and pricing; record dated sources and confirm access without exposing credentials.
- [-] Runtime scaffolding implemented; locked Ruff and 60 tests pass. Fresh build/start pending; see docs/evidence/m1-runtime.md.
- [x] Implement Pydantic analysis validation aligned with the checked-in schema; reject nonfinite values, invalid evidence and unsupported output shapes. Evidence: `docs/evidence/policy.md` (58 focused tests).
- [x] Implement billing normalization/arithmetic and pure routing/escalation policy. Evidence: `docs/evidence/policy.md` (58 focused tests).
- [x] Turn the controlled cases into executable tests; add monetary normalization and schema-validation cases. Evidence: `docs/evidence/policy.md` (58 focused tests).
- [x] Smoke-test the exact schema against the selected real model; record usage and any schema adjustments.

Gate: locked environment starts, policy/validation tests pass, exact model schema works on a real response. No unsupported claims of full application functionality.

## M2 — Working vertical slice

- [x] Persist incoming requests, attempts, accepted analyses and derived decisions with migrations. Offline verification: docs/evidence/m2-backend.md; real concurrency/queue acceptance pending.
- [x] Implement canonical webhook, principal-scoped idempotency, session/CSRF and bearer-token authentication. Offline verification: docs/evidence/m2-backend.md; real concurrency/queue acceptance pending.
- [x] Publish after commit, atomically claim tasks, call the model outside transactions, and persist result/completion atomically. Offline verification: docs/evidence/m2-backend.md; real concurrency/queue acceptance pending.
- [x] Implement status and export endpoints and safe error envelopes. Offline verification: docs/evidence/m2-backend.md; real concurrency/queue acceptance pending.
- [x] Build visual tester that posts to the webhook and displays asynchronous progress/results.
- [x] Preserve the five assessment inputs verbatim; sample loader uses the same intake service.
- [ ] Process all five inputs through the real container stack and model; save complete output records.

Gate: form submission automatically reaches a persisted/exportable result through Redis/Celery; all five records are real and complete.

## M3 — Reliability and review experience

- [-] Add bounded retries, explicit timeouts, sanitized failures, cost tracking, and eligible manual retry.
- [x] Protect concurrent duplicate ingestion/task deliveries and accepted results with meaningful tests.
- [x] Verify publication-failure visibility and operator-assisted republication without resetting retry budgets.
- [x] Test transient/permanent provider errors, invalid output/refusal, retry exhaustion, permissions and CSRF.
- [x] Build inbox/detail and separate Human Review queue with original text, evidence and decision reasons.
- [x] Test browser interaction and capture screenshots for tester, completed request, escalation and failure states.

Gate: core behavior and implemented recovery paths are verified in the real stack; simulated faults are labeled, and worker-crash recovery limits are documented.

## M4 — Evaluation and prompt optimization

- [x] Define benchmark record format and metrics before generation; keep policy fixtures outside the 50-message count.
- [x] Generate and review an initial small batch against the written rubric; resolve label ambiguities.
- [-] Complete 50 cases: 5 supplied acceptance, 25 development, 10 validation, 10 locked final test. Keep related scenario families within one split.
- [x] Validate scorer behavior with known good/bad predictions before live benchmarking.
- [-] Run a baseline; score category/priority, entities, semantic signals, summaries and output validity separately.
- [x] Record end-to-end destinations, missed/unnecessary escalations, incorrect automatic routing and automation coverage.
- [x] Iterate versioned prompts on development cases; select candidates using validation. Record experiments, usage, latency and observed regressions.
- [x] Freeze prompt/model/schema/policy; run locked final test once. Disclose any reuse after changes.
- [x] Save predictions, run metadata and an honest report with counts/denominators, unknown costs and limitations.

Gate: reproducible results show measured behavior rather than asserted accuracy; required five outputs match the chosen final configuration.

## M5 — First complete submission checkpoint

- [ ] Finish tested clean-checkout setup and reviewer commands in README.
- [x] Write prompt rationale and separate one-to-two-page architecture document: docs/submission/.
- [x] Record real AI-assisted development decisions, mistakes caught and corrections: docs/submission/README.md.
- [ ] Record a 4–6 minute demonstration covering all five inputs, actual escalation, export, and verified recovery if useful.
- [ ] Check JSON outputs, documentation and recording against one consistent code/prompt/model version.
- [ ] Save/tag a submission-ready checkpoint and push it.

Gate: all Section 4 assessment deliverables are ready to share even if optional enhancements stop here.

## M6 — Optional improvements and final packaging

- [ ] Add authorized human approval/correction with preserved original predictions, reviewer audit and recomputed effective routing.
- [ ] Add queue filters and polish grounded in screenshot/browser findings.
- [ ] Consider advanced recovery or a second model only if demonstrated weaknesses justify the work.
- [ ] Re-run affected regression checks; regenerate final evidence after accepted changes.
- [ ] Prepare the submission email and access checklist. Send/share with the recruiter only on explicit instruction.

## Agent coordination

After executable contracts stabilize, independent work can cover application/UI, evaluation tooling, and dataset generation/review. Assign file ownership and acceptance criteria before delegation. One integration owner reviews changes, resolves contract conflicts, runs integrated checks and updates this tracker. Independent dataset review should label actual text, not trust the generator's intended label. Agents must not change shared schemas/policy silently or claim unperformed checks.

## Decision and progress log

| Date | Change | Evidence / implication |
| --- | --- | --- |
| 2026-11-07 | Locked webhook-first delivery, latest stable Django preference, 50-case split and $83 API ceiling | User decisions recorded in assessment plan |
| 2026-11-07 | Created contracts, strict schema and 25 policy cases | JSON/structure checks passed; implementation and live evaluation pending |
| 2026-11-07 | Created execution tracker and repository introduction; published private repository | Verified remote baseline `2eedbbe`, private visibility, and default branch `main`; staged whitespace check passed |

## PR #2 independent integration review

Remote functional head verified: `7a7ac6db7c4f3cdf3887bee8b2c86210eba64ef8`. Independent reviewer reported no blockers and 58 passing tests using the command in docs/evidence/policy.md. Probes verified $1240 versus $980/month yields $260 Billing; exact 500 automatic/500.01 review; signed undercharge; confidence .699999 review/.70 automatic; monetary evidence normalization; rejection of unsupported evidence, Unknown basis, mutated and bypass models. Integration rerun: 58 passed in 0.08s. Documentation-only integration. Semantic attribution, live provider and runtime integration remain pending.

## Provider implementation checkpoint — 2026-11-07

- [x] Implement single-request Responses adapter and triage_v1 prompt; contextual validation and pipeline-facing contract documented in docs/prompts.md.
- [x] Offline SDK-envelope/provider and policy verification: 63 tests passed; see docs/evidence/provider.md.
- [ ] Live exact-schema gate and initial model/pricing selection remain pending, not replaced by mocks.
- Explicit user approval now permits disclosed synthetic assessment/benchmark payloads within cumulative $83; provider task capped at $3 and five supplied messages. No live calls made in this checkpoint.

## Integration checkpoint
Runtime/policy/provider/backend checkpoint implemented; M2 remains incomplete. Sample commands, UI, and five live outputs remain pending. Independent review of PR4 366dfab and PR5 c14c69f reported 69 passing tests, Django check, and two offline SDK-validated adapter/process probes. Preserved the parameterized probe in tests/test_provider_pipeline.py.

Before reliability claims: verify live strict schema/model/pricing, successful session-CSRF flow, PostgreSQL concurrent duplicates/task deliveries, actual Redis publication/retries. Early retry delivery returns without republishing (tasks.py lines 27-28), relying on broker countdown; test that behavior in Redis. No retry design changes in this integration.

## UI checkpoint — 2026-11-07

- [x] Implement authenticated tester, inbox, persisted Human Review filter, detail/evidence/attempts and completed export navigation; see docs/evidence/m2-ui.md.
- [x] Verify successful session+CSRF webhook ingestion with mocked provider, missing-CSRF rejection, auth redirects, POST logout, incomplete export and escaped content. Full locked suite: 72 passed; Ruff/Django/migration checks passed.
- [ ] Browser interaction/screenshots: local Chrome blocked by crashpad socket sandbox; no visual acceptance claimed.
- [ ] Actual queued/live/clean-build/benchmark gates remain pending. Manual retry API is absent; no UI retry workflow invented. Human review remains read-only.

PR #6 correction: actual c61e539 PR branch checked out before tests; lifecycle suspend/restore and single-flight protection added. Dependency-free executable JS regression passes; locked suite 72 passed and Ruff/Django/migration checks clean. See docs/evidence/m2-ui.md. Escalated Chrome startup works, but interactive browser fixture acceptance/screenshots remain pending; do not merge this checkpoint yet. All prior live/provider/queue/benchmark gates retained.

PR6 browser checkpoint: real Chrome login/tester POST/pending-to-completed/detail/Back/mobile/network-failure Resume executed with mocked provider. Screenshots and exact remaining acceptance gaps: docs/evidence/pr6-browser/execution.md. Keep PR open pending full lifecycle/fault acceptance.

PR6 bounded UI checkpoint follow-up: fake-timer lifecycle/60-poll expiry/Resume and response-loss idempotency regressions pass; actual Chrome accepted-then-aborted response retry yields two identical POSTs and one DB row. Actual Back reload works; persisted pageshow is simulated (no actual bfcache observed). Python 73 passed; Ruff passes. Live provider and real queue/runtime gates remain separate later milestones. See docs/evidence/pr6-browser/execution.md.

## Sample command checkpoint — 2026-11-07

- [x] Preserve original five inputs; idempotent intake-backed load_samples and guarded deterministic export_samples implemented and tested.
- [x] Offline checks: 74 pytest tests, Ruff, Django check, migration drift check and two JS harnesses pass.
- [!] Live schema and five-message queued acceptance pending secure credential (request timed out) and Docker socket access. No paid calls, task spend $0; no output artifact fabricated. Details: docs/evidence/m2-live.md.


## PR7 integration checkpoint
Reviewed head: df5fa91a28fbca43601cfca1712aceeda93846dc. Parent-supplied independent review: no blockers; original Downloads DOCX five strings matched; shared acceptance service/stable principal keys; SQLite five first dispatches, zero repeat dispatches, conflict without extra dispatch; ordered export completion/result/source/message guards; 74 locked tests and Ruff/Django/no migration drift passed. This proof is supplied review evidence, not independently repeated DOCX or historical spend verification.

Fresh implementation verification: 78 locked tests pass, Ruff passes, Django check passes, no migration drift. Added actual task pipeline with mocked provider and full persisted record export equality in sample order; missing accepted result and mismatched source/message fail with zero JSON written, including after earlier valid samples. README exports to temporary file and renames only on success. No OpenAI calls. Live provider, real queue and PostgreSQL acceptance remain pending; historical spend is not independently verified.

Live acceptance attempt 2026-11-07: incomplete; see docs/evidence/live-acceptance.md.
One retained real schema probe succeeded; five pipeline calls yielded one failure
and four completions, but ephemeral records/usage were lost before guarded export.
Actual sample export, queue/Postgres, benchmark and clean-start gates remain open.

### 2026-11-07 recovery inspection

PR8 expected head verified. See `docs/evidence/live-acceptance.md` recovery
inspection. Zero complete live sample records recovered; surviving browser DB
records are explicitly mocked. Known subtotal $0.0006268, total unresolved.
No paid requests performed. Durable runner and fault tests are still pending;
next paid execution is blocked pending reliable persistence and budget bounds.

## Durable acceptance runner
Implemented `apps.triage.acceptance`: explicit persistent directory, fsynced append-only
reservation/result journal, exclusive writer lock, conservative Decimal reservations,
resume and atomic ordered five-result export. CLI defaults to offline dry run.
Injected execution requires a bound-enforcing adapter and documented reconciled
history/prices. Existing uncapped OpenAI adapter intentionally cannot be used directly.
All reservations remain charged even when usage exists (conservative accounting).
Historical known subtotal $0.0006268 and five unknown calls remain unresolved;
no live acceptance or paid inference was performed. Automated fault checks added.

Validation: locked dependencies installed; 84 pytest tests passed (6 staticfiles warnings), Ruff clean, Django check clean, CLI dry-run pending=5.

## PR8 bounded adapter checkpoint
Implemented SDK output cap, configuration-bound adapter with fail-closed input-proof hook,
preflight before reservations/invocation, and durable provider usage before secondary
validation. Existing exclusive runner lock and retained reservations remain in force.
Offline validation: explicit /tmp uv cache/environment, locked pytest 86 passed (6
warnings), Ruff clean, Django check clean, dry-run five pending. Initial pytest lacked
DJANGO_SECRET_KEY; rerun used a synthetic offline key and /tmp SQLite database.
Remaining: implement and substantiate actual input token proof (hook is not a proof),
expand requested durable fault coverage, and reconcile historical five-call costs.
No live calls or credential reads. This checkpoint is partial, not acceptance complete.

### Application model selection (2026-11-07)

User-selected default: `gpt-6.1-terra`, replacing the prior planned GPT-4.1 mini default. Historical actual mini run records remain unchanged.

Official evidence: https://developers.openai.com/api/docs/models/gpt-6.1-terra lists Responses and Structured Outputs support, 1,050,000 context, 922,000 maximum input and 128,000 maximum output tokens. Reasoning supports none/low/medium(default)/high/xhigh/max. Adapter explicitly selects none with the existing 4096 output cap, and sends no sampling parameters.

https://developers.openai.com/api/docs/guides/structured-outputs documents strict JSON schema support and schema restrictions. Exact application schema server acceptance and account access remain UNVERIFIED; no model listing, secrets, or inference calls were used here.

https://developers.openai.com/api/docs/pricing lists Standard short context (<=272K input) rates per million: input $1, output $5, cached input $0.05, cache writes $1.25 (30m)/$2.50 (12h). Long context input $2/output $7.50. Regional processing +10%, Fast 2x. Future budget runner configuration must use these model-specific rates with conservative allowance for cache writes/tier, output <=128K, and verified input bounds. The runner has explicit prices rather than a model catalog; old mini rates must not be reused. Historical accounting and exact input-bound proof remain mandatory gates before execution.

PR8 final implementation: default bounded adapter reserves full Terra 1,050,000
context tokens (deliberately counts shared output space twice), requiring at least
$2/M input and $7.50/M output. At cap 4096, reservation is $2.13072/request,
$10.65360/five: exceeds $3 and must reject; fits $83 before historical reserves.
Official model page verified 2026-11-07: short $1/$5, >272K full-request
2x input/1.5x output; no cached discount assumed. Standard service only.
https://developers.openai.com/api/docs/models/gpt-6.1-terra
Historical mini theoretical five-call ceiling is
5*(1047576*.4+32768*1.6)/1000000 + .0006268 = $2.3579228.
This is a conditional maximum, not measured spend; model/count provenance still
requires independent evidence audit before reconciliation. Historical records unchanged.
https://developers.openai.com/api/docs/models/gpt-4.1-mini
No live/account/schema acceptance established. Full locked pytest: 72 passed,
15 PostgreSQL connection setup errors. Ruff and Django check passed; dry run
reported five pending. Remaining acceptance audit/tests and PR body unfinished.

## PR8 integration repair
Integrated reviewed 797d267 into actual PR8 ancestry in prepared checkout; other
worktrees and stray remote branch preserved. Added six regression cases for premium
fallback floor, finite prices, model/context bounds, reservation ordering and immutable
resume. Full SQLite offline suite 93 passed (six staticfiles warnings); Django check,
migration drift check, dry-run pending=5 and whitespace check clean. See
 docs/evidence/live-acceptance.md for commands, corrected premium reserve and precise
historical evidence gap. No PostgreSQL or live acceptance claim; no inference calls.
# PR1 offline completion

Completed the 50-case label-quality audit (`evals/review.jsonl`), canonical PR9
export adapter and current-main integration. Full offline suite: 105 passed;
dataset validation and Ruff passed. Exact commands, review comments, semantic
overlap and live-benchmark limitations: `docs/evidence/pr1-completion.md`.


PR8 integration: independent review reported no blockers at exact head
9b19a6a606cf67f77f82caa9efb30bc3ccabed14; reported offline proof: 93 tests,
Ruff, Django checks and migration checks on SQLite. Merged main: 2b42ec3.
Review limits: invalid raw responses were lost before validation; CLI lacked live execution.
Follow-on command implementation in progress; command wiring tests remain required.
No paid calls or credential reads performed. Historical account reconciliation,
live schema acceptance and PostgreSQL/Redis/Celery gates remain outstanding.

PR9 finish: command SDK tests, failure accounting and metadata limits implemented.
Offline proof: docs/evidence/pr9-finish.md. Account/schema/queue acceptance pending.
Historical planning reservation remains conditional, not actual cost.

PR9 export repair: shared application record builder wired into durable acceptance
journal. Offline suite: 107 passed. Live provider and DB acceptance remain pending.

PR9 substantive regression coverage: `test_command_assessment_billing_and_outage_regression` and `test_command_full_export_matches_canonical_builder` exercise five source-shaped SDK responses and canonical full-record parity. Existing resume coverage retained. Offline validation: 109 tests passed; Ruff passed. No application bug exposed; no live calls.

PR9 runner/provider missed-review remediation (offline):
- https://github.com/ahnaineh/arcvault-ai-triage/pull/8#discussion_r4501752720: hash actual loaded prompt/schema text into inference identity; compare reservation fingerprints before cached reuse or spending. New-run/reconciliation guidance on mismatch. `test_artifact_change_blocks_resume` covers partial and complete runs, both artifacts. Existing immutable accounting config and uncertain-reservation protections retained.
- https://github.com/ahnaineh/arcvault-ai-triage/pull/8#discussion_r4501784659: Terra conservative pricing enforced independently of verifier callback. `test_wrapped_bound_price_floor` rejects zero/underpriced wrapper and accepts valid pricing.
- https://github.com/ahnaineh/arcvault-ai-triage/pull/9#discussion_r4501813739: HTTP evidence sink OSError carries sanitized captured usage; `test_http_write_failure_retains_usage` proves failed ledger usage, reservation retention and no secret persistence.
Validation: locked SQLite suite 117 passed (six missing-staticfiles warnings); Ruff, Django check, migration drift and diff whitespace passed. Initial suite exposed mock fixture's fabricated inference_identity; fixture explicitly declares None, then full suite passed. Full-export billing/outage/canonical parity baseline retained. No live calls or credentials. Historical reservation remains 6.22326144, actual unknown. Pending application policy/config/UI and evaluation findings belong to parent/other work and remain pending.
### GitHub missed-comment remediation

Read `/tmp/pr-audit/audit.md`, fetched all five original review bodies, and compared
current source at main 2b42ec3039df34b2a6d95abddac7fe1d33d4043a. This focused branch
owns Celery startup, billing precision/evidence, DB credentials, and tester timeout.
Acceptance/provider and eval findings remain assigned to other scopes; no changes
or comment replies/resolutions are made here. See docs/evidence/pr-comment-remediation.md.

PR9 final integration: PR10 merged cdcbf21580140d7f5d2244a0c20af15c5138a9c5.
Original eight findings closure preserved across this merge in this tracker and
 docs/evidence/pr-comment-remediation.md. New finding
https://github.com/ahnaineh/arcvault-ai-triage/pull/9#discussion_r4501882363
is covered by test_execute_then_dry_identity: shared artifact hashing, zero pending
after mocked execution, changed prompt/schema each five pending, no extra SDK client/calls.
Focused command tests 24 passed; combined SQLite suite 129 passed (six staticfiles
warnings), Ruff/Django/migration checks and all three JS harnesses passed.
No paid calls, credentials, PostgreSQL, queue or live acceptance verified. Plan states retained.

PR1 integration: current main including PR10/PR9 merged semantically; prior plan
states and reviewed evaluation changes retained. Malformed entity finding
https://github.com/ahnaineh/arcvault-ai-triage/pull/1#discussion_r4501441540
fixed by constructing metric tuples only after schema validation. Regression covers
list/dict type/value and a subsequent good prediction; invalid records fail and
report continues. Focused eval/export adapter 13 passed; 50-case validation and Ruff
passed. Initial test commands named nonexistent adapter files; corrected above.
No repeated label audit or live calls. Parent-supplied independent 50-label/seven-thread
review retained as supplied evidence. Latest comments add substantive findings
r4501893516 (development-17 unresolved billing reason) and r4501893519 (processing
measurements adapter); PR1 intentionally remains open pending their assessment.


PR1 final feedback (offline foundation, 2026-11-07)
- https://github.com/ahnaineh/arcvault-ai-triage/pull/1#discussion_r4501893516: valid; development-17 now includes billing_comparison_unresolved before conflicting_intents. test_duplicate_payment_reason_matches_policy verifies current application policy order.
- https://github.com/ahnaineh/arcvault-ai-triage/pull/1#discussion_r4501893519: valid; adapter maps estimated_cost only when unknown_cost is false, sums all recorded attempt latencies, and preserves null for missing latency or unknown cost. test_processing_measurements covers retries, known cost, unknown cost and incomplete/empty attempts.
- Main a79bc2a48d24c6c29d73473db291637585a4d540 already included in PR head; no compatibility merge required. Existing tracker retained.
- 15 focused evaluation/adapter tests passed; 50-case dataset validation passed; Ruff passed. No application/provider/runner edits, live calls or benchmark execution.

## Network acceptance follow-up
Five Terra calls completed with raw usage and durable file evidence in docs/evidence/terra-network-20261107. Escalated HTTPS 401 established network access. Historical uncertain reservations retained; total 75.92876544 < 83. Invoice $260 requirement remains unmet (missing billed period); outage Human Review verified. No queue/Postgres acceptance.

## PR12 offline invoice acceptance correction
Persisted evidence: docs/evidence/terra-network-20261107/offline-policy-review.md
and assessment_outputs.policy-1.1.json; reproducible with
python -m scripts.reprocess_invoice_evidence. Original raw responses and records
retained unchanged. Five schema/source reviews complete; invoice apparent 260 /
Billing under declared monthly/component assumptions, outage Human Review.
Invoice priority remains model Low versus illustrative plan Medium, documented.
This is offline canonical record acceptance, not queue DB or new inference.

## PR12 narrow implementation follow-up (2026-11-07)
Original finding https://github.com/ahnaineh/arcvault-ai-triage/pull/12#discussion_r4501937202
-> shared exponent-aware _subtract_exact in both billing branches; regression
 tests/test_invoice_saved.py::test_direct_invoice now includes unequal scales,
 yielding 99999999999999999999.999999999999999999999 exactly.
User-verified offline-review grading blocker -> corrected invoice and Okta Low
versus evals/dataset.json Medium to ERROR: priority 3/5, derived routing 5/5.
No full quality pass claimed. Raw outputs/priorities unchanged. Offline
scripts/reprocess_invoice_evidence.py refreshed only derived policy code hashes.
Current comments, reviews, inline comments and threads inspected: sole bot finding
is the URL above, no additional findings. Focused pytest tests/test_policy.py
 tests/test_invoice_saved.py: 77 passed. Ruff on policy, regression and reprocessor:
PASS; git diff --check PASS. UV_CACHE_DIR=/tmp/arcvault-uv and
UV_PROJECT_ENVIRONMENT=/tmp/arcvault-infra-verify-venv; synthetic key and explicit
SQLite /tmp/pr12-unit.sqlite. No inference, credential or infrastructure operations.
## Real infrastructure acceptance (2026-11-07)

Verified latest main 7149968 including PR10 using existing images, isolated PostgreSQL
18.3/Redis 8.6.1/Celery worker and authenticated real HTTP. Synthetic inference only.
Concurrent intake, duplicate delivery, DB/export parity, bounded transient retries,
permanent failure, publication failure/operator republish and early-countdown
replacement verified. Fixed early delivery dropping replacement publication; source
review required. Full offline suite 144 passed. Reproducible opt-in harness and precise
limits: docs/evidence/infrastructure-acceptance.md. Clean image build, production
startup and live provider acceptance remain pending; M1/M2 full gates stay open.

## PR13 cleanup ownership completion (2026-11-07)
Transferred the prior agent's uncommitted run.sh and test_cleanup.sh read-only from
/home/ahnaineh/.t3/worktrees/Aspire/t3-bc33572a. Unique UUID names and tracked
created IDs restrict cleanup to this invocation, including docker start failure.
Current checks: bash -n tests/infrastructure/{run,test_cleanup}.sh; bash
tests/infrastructure/test_cleanup.sh PASS; UV_CACHE_DIR=/tmp/arcvault-uv
UV_PROJECT_ENVIRONMENT=/tmp/arcvault-infra-verify-venv DJANGO_SECRET_KEY=synthetic
DATABASE_URL=sqlite:////tmp/pr13-unit.sqlite uv run pytest -q -k 'retry or early':
2 passed, 142 deselected (one existing staticfiles warning); git diff --check PASS.
Prior real HTTP/PostgreSQL/Redis/Celery proof is retained in PR13's Executed proof
section at head 420b7bf4c23e3cba073ccac9a188f3ee996b6de0 and supplied prior-agent
handoff; this completion did not independently rerun that harness. Synthetic provider,
existing images, resources cleaned; no live inference or image builds/pulls.
Current GitHub comments/reviews/inline/threads inspected: sole finding r4501931951.

## Benchmark continuation audit — 2026-11-07

Fetched and fast-forwarded the clean implementation worktree to main af290b7.
Original five records and raw journals remain unchanged. Runner now attaches raw
response events to their request reservation and case before validation, improving
reconciliation evidence without weakening unresolved-attempt blocking.

Paid benchmark remains pending: current full-context adapter reserves 11.617584
per call. Recorded five completed calls total 4738 input / 1026 output; conservative
usage estimate 0.069047 is not actual billed cost. Historical 6.22326144 and
uncertain connection attempt 11.617584 remain reserved. Existing maximum retained
reservation total is 75.92876544. No paid calls performed in this continuation.
Next execution requires verified bounded-input accounting and durable completed
usage reconciliation across benchmark phases; simply lowering config bounds fails
the existing adapter verifier. Final test labels were not opened for tuning.

Secure credential request returned timed_out; no credential was read or copied.
Offline focused acceptance suite: 24 passed with explicit SQLite and synthetic
DJANGO_SECRET_KEY. Ruff and diff whitespace checked after binding sink identifiers.

## PR14 benchmark execution — 2026-11-07

Completed usage reconciliation and serial per-call budget checks in the existing
Runner. Missing/invalid usage and uncertain completion retain maximum reservations;
reconciliation events are append-only and idempotent. Original five raw journals
remain untouched; reconciliation.json binds the source hash and accounts .069047
as a conservative estimate, never actual billing. Both uncertain reservations remain.

Implemented run_benchmark over the same Runner, canonical export adapter and scorer:
ordered baseline/development/validation/test/assessment, shared accounting lock,
immutable phase identities, explicit freeze, resumable completed cases. Baseline
25 and single revised-prompt development 25 completed; validation 10 completed.
V2 priority/entity clarification used development failures only; no policy changes.
Validation category/routing 9/10; priority/entities/signals/schema 10/10. Final test
still unopened at this checkpoint. Earlier v2 exports carry legacy v1 display labels;
reservation inference hashes and manifests identify actual prompt. Corrected selected
prompt labels and exported hashes before final freeze; originals remain unchanged.

## PR14 final benchmark checkpoint — 2026-11-07

- [x] Existing runner extended with completed-usage reconciliation, serial pre-call
  reservations, durable raw evidence and one shared ledger across all phases.
- [x] 75 paid calls completed: baseline25, revised development25, validation10,
  frozen final test10 once, final assessment5. No SDK retries or extra prompt revision.
- [x] Final artifacts and detailed limitations: docs/evidence/benchmark-20261107/README.md.
  Final test category/routing9/10; final assessment routing5/5, priority3/5 and exact
  entities2/5. Original outputs preserved. Prior narrative original-five priority3/5
  is inconsistent with current login-High label; exact current-rubric rescore2/5.
- [x] New usage81054 input/12677 output, conservative estimate1.1007645; original-five
  estimate.069047 plus uncertain reservations17.84084544 yields accounted19.01065694.
  Actual billed cost remains unknown; ceiling83 respected at every reservation.
- [x] Offline suite169 passed; Ruff and diff whitespace clean. Phase/freeze/resume,
  missing usage, repeated reconciliation and exhaustion regressions included.
- [x] User-requested Astra prompt review received after freeze; valid rubric conflicts
  and coverage/tie-break gaps documented as follow-up. Frozen prompt unchanged.
- [ ] Independent human summary-faithfulness audit remains pending. Assistant manual
  review is disclosed separately; no synthetic human-review scores were supplied.

This checkpoint completes benchmark execution, not production/submission acceptance.

## User-authorized Luna comparison

V3 consolidates the written priority rubric (review is independent), active outage
precedence, error-code extraction, general current-action intent, first-mentioned
mixed-intent tie-break and nonnumeric discrepancy boundaries from Astra/development
review. V1/V2 and original frozen metrics remain unchanged. Dataset/scorer labels
are unchanged despite known rubric conflicts. No final-test errors used to tune v3.
Official API docs verify gpt-6-luna, high reasoning, 1.05M context, Responses and
structured outputs; model page and pricing page read 2026-11-07. Comparing Luna
high vs Terra none on identical v3/schema/all50, explicitly reused comparison set.
Output cap25000 for both (includes reasoning tokens); no SDK retries. Existing
Runner and accounting journal reused, with root lock and immutable model histories.
Application default unchanged pending measured tradeoffs.

## V3 paired comparison complete — 2026-11-07

- [x] Official public API gpt-6-luna/high/Responses/strict output support and pricing
  verified; no coding-catalog substitution. One V3 revision from rubric/development
  review only; originals and frozen75-call evidence unchanged.
- [x] Paired100 calls completed (same50/model): Luna high vs Terra none, cap25000,
  zero retries/truncations. Explicit reused comparison set, not another holdout.
- [x] Luna15 nonverbatim-evidence rejections retained unchanged; terminal failures
  added to runner with explicit code-only amendment so cases are never resent.
  All15 maxima remain reserved. First failure latency missing and disclosed.
- [x] Terra category49/50, priority39/50, exact entities44/50, routing44/50,
  application validity50/50. Luna35/50,32/50,29/50,30/50,35/50 respectively.
  Raw structural schemas50/50 both; assistant summary review separated from pending
  independent human review. Paired wins/regressions and all split metrics retained.
- [x] Luna standard-price usage estimate.0169297 vs Terra.103802; actual billing
  unknown. Project conservative accounted39.33219774 of83 includes prior reservations
  and fifteen full Luna failed reservations. Reasoning11232 included in output21601.
- [x] Recommend retain Terra default: Luna cheaper but slower with15 invalid analyses.
  Application now selects V3 prompt via allowlisted OPENAI_PROMPT_VERSION, model
  default remains Terra. Exact run/source/default-wiring distinction documented.
- [x] 174 offline tests pass; Ruff/diff whitespace clean. Full evidence, source
  identities, raw usage/journals, costs, p50/p95, caveats and report builder:
  docs/evidence/comparison-v3/README.md and protocol.md.

### Documentation and failure audit follow-up

Verified prior75 and paired100 calls each have unique reservations/raw/terminal
records; original source journal hash unchanged. Documented all15 Luna failures
at field level:28 nonverbatim excerpts,16 outer-curly-quote additions and12 generated
explanations;6 quote-only cases,9 other/mixed. API/JSON succeeded; exact-source
application validation rejected model output. Distinguish that from semantic
classification error and the independently fixed initial harness-stop behavior.
Verified supplied five are byte-equal to dataset assessment-01..05, array rows1..5;
50=assessment5+development25+validation10+test10. Mapping and reproduction audit
are in docs/evidence/comparison-v3/failure-analysis-and-dataset.md.

PR review follow-up: fixed compare_models dry-run history carry-forward by reading
preceding existing model journals in both execution and dry-run modes. Regression
runs offline inspection after both model configurations exist, proves zero extra
provider calls and byte-identical JSON/journals. Frozen live results unchanged;
code identity guard still rejects mismatched execution snapshots as intended.

## Prompt integration closure

Confirmed acceptance/app prompt mismatch independently of the earlier accounting
fix. Shared selector now uses V3 by default across provider, bounded adapter,
ArtifactIdentity, acceptance, benchmark and comparison; explicit legacyV1 supported.
Removed imperative command prompt mutation. SDK-request hash/resume/version-change
regressions added. V3 text remains4193bytes/543words with original measured hash;
no semantic revision or paid calls. Existing evidence retains actual executed prompt.
Offline paired raw-to-prediction and arithmetic reconciliation recorded in
comparison-v3/closure-reconciliation.json; historical/failed maxima retained,
project accounted39.33219774, maximum replayed prefix51.27866524 below83. Reused
reviewer scorer-equality/57-check evidence; no new inference. Summary review remains
pending independent human adjudication; earlier assistant observations are narrative,
not durable case-level completed manual review. Details: integration-closure.md.

Final combined closure checks:177 tests passed; Ruff, Django check, migration drift
and diff whitespace clean (six existing missing-staticfiles warnings). No paid calls.

## Final V4 checkpoint and test consolidation

User authorized compact V4 default and exactly one final50-case Terra comparison. Complete evidence and limits: docs/evidence/final-v4/README.md. 50calls, zero retries/invalid outputs; raw-to-export-to-prediction/scorer reconciliation passes. Result mixed versusV3; all original measurements preserved. No more prompt tuning planned. Accounting39.99125174/83 including retained reservations; actual billing unknown.

PR15 merged into PR14 base after source review and no-finding bot review. Consolidated literal export/resume checks and parametrized HTTP/success disk failures; distinct safety seams preserved. See docs/evidence/test-suite-review.md. Combined final177tests and Ruff pass. Corrected prior stale top-level checkpoint; older numbered milestones retain limitations for human summary review, semantic split independence and combined full-stack/live-provider demonstration.

PR14 comments: discussion_r4502097330 comparison dry-run accounting fixed previously; discussion_r4502138128 cross-phase prompt selection now lives outside immutable accounting config, with V1-to-V2 regression. No model calls for either harness fix.

## Submission packaging verification — 2026-11-07

- [x] docs/submission contains architecture, actual prompt rationale, AI lessons, final-five index, demo commands, recording script and email draft.
- [x] Current main verified at a9c0d640987e13813b93dc612543756f3aee4a48. PR14 inline findings inspected: comparison dry-run accounting and cross-phase immutable ledger; final evidence records their fixes.
- [x] Django check passed using existing locked environment; Compose config passed after copying .env.example to ignored .env. Final JSON parses as five records; git diff --check passed. No full test rerun for prose changes.
- [x] Isolated cached-image startup: ARCVAULT_INFRA_OPT_IN=yes bash tests/infrastructure/run.sh passed, including HTTP concurrency, duplicate deliveries, export parity, transient/permanent errors and republication. Synthetic provider only; owned resources cleaned by script.
- [!] Clean image build deferred: root 98% used, approximately 2 GB free; Docker /var/lib/docker has 2.314 GB images and 1.455 GB volumes with existing ArcVault/RPiDoor services. No deletion, prune or downloads.
- [ ] Essential handoff: review/merge packaging PR, verify private reviewer access, choose and complete recording or declared live interview demonstration, final version/tag check. New model inference requires renewed authorization.
- [ ] Optional: audited human correction and queue filters; not submission gates.

Submission prose review: shortened AI lessons, removed internal agent instructions from reviewer setup, and distinguished model-call costs from authorization language. Architecture and links checked directly; clean build and combined live-model queue recording remain unverified.

## Isolated real-provider demo startup — 2026-11-07
Actual Dockerfile/locked image build and Compose startup passed at b4368bbc.
Owned project `arcvault-demo-20261107`, localhost:18407; fresh PostgreSQL,
Redis AOF volume, migrations, health, worker ping and authenticated tester/CSRF
verified. Terra / triage_v4; no inference or sample loading performed. Runtime
commands, startup log, resource IDs and snapshots: `/tmp/arcvault-demo-20261107`.
Credentials remain outside repository. Services intentionally left running.
Recording and five serial real webhook submissions remain for parent operator.

## UI workspace redesign
- Updated prepared checkout to main fec5475; preserved submission/demo evidence.
- Routing-first detail, readable billing/evidence, expandable technical metadata and logs; shared compact workspace styling for login, tester and inbox.
- Validation and outstanding browser acceptance: docs/evidence/ui-redesign.md.

## UI and narrated-demo revision

- UI review complete: routing-first detail, visible confidence percentage and all required output fields; readable billing, source evidence and expandable technical metadata.
- Verified 178 tests, Ruff, three JS harnesses, real desktop/mobile and keyboard checks. Fixed single-worker idle-connection stalls with Gunicorn threads. Evidence: docs/evidence/ui-redesign.md.
- Narration generated with OpenAI speech; new recording and final audio synchronization in progress. Earlier captioned video remains historical until replaced.

## Final narrated recording

- Replaced the captioned video with a first-person AI voice-over and the redesigned UI. One fresh live login submission plus four explicitly saved live results; no repeated five-case benchmark.
- All required metrics are visible, including confidence percentage, core issue, urgency and explicit Human Review status. Narration is synchronized to real UI actions.
- Full video/audio decode, speech transcription, frame inspection, runtime hashes and export checks passed. Source evidence and previous outputs are preserved. Current total accounting including speech allowance: $52.69598874/$83; actual billing unknown.

## Final video and reviewer login — 2026-11-07

Completed natural narration recut (2:15, no subtitles), readable JSON export, documented admin / admin local login and concise current setup docs. Full suite: 181 passed; Ruff passed; final UI/check/migration checks passed. Video decode and transcript checked. No new triage inference. See `docs/evidence/final-demo-checks.md`. Final user playback and repository visibility at submission remain user handoff steps.

## Submission presentation cleanup — 2026-11-07

Added source-checked benchmark tables and model-choice rationale. Removed the email draft from the repository and saved it locally. Removed cost estimates from submission-facing prose and recording metadata; original benchmark journals remain historical evidence. Local submission ZIP is generated from the published commit, excluding Git metadata and private runtime files.
