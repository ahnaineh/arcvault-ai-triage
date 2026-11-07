# ArcVault delivery work plan

This file is the source of truth for execution status. Update it in every implementation commit that changes task status, scope, acceptance evidence, or blockers. Do not mark a task complete from generated code alone.

Design rationale: [ASSESSMENT_PLAN.md](ASSESSMENT_PLAN.md). Interface and policy specification: [docs/CONTRACTS.md](docs/CONTRACTS.md). If these documents conflict, record and resolve the decision here, then update the affected specification before dependent implementation.

## Current checkpoint

Backend checkpoint: core persistence/API/tasks implemented; 64 SQLite/offline tests pass. See docs/evidence/m2-backend.md. M2 remains active pending frontend, samples and real queued/provider acceptance.


- Phase: M1 partially implemented: validation and policy verified locally; runtime integration and live provider acceptance pending.
- Working deadline: November 8, 2026, as stated by the candidate.
- API budget: cumulative ceiling of $83 before credits; no paid model calls performed by this planning work.
- Scope: webhook-first intake, visual tester, inbox/detail and review queue, one structured model call, deterministic policy, persistent outputs, focused reliability, 50 reviewed synthetic cases, submission evidence. Human correction remains an optional enhancement after the first complete submission checkpoint.
- Repository: [ahnaineh/arcvault-ai-triage](https://github.com/ahnaineh/arcvault-ai-triage), private, default branch `main`.
- Blockers: none known. Exact Python/package/model compatibility remains to be verified.

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
- [ ] Select an initial OpenAI model using current documented availability and pricing; record dated sources and confirm access without exposing credentials.
- [-] Runtime scaffolding implemented; locked Ruff and 60 tests pass. Fresh build/start pending; see docs/evidence/m1-runtime.md.
- [x] Implement Pydantic analysis validation aligned with the checked-in schema; reject nonfinite values, invalid evidence and unsupported output shapes. Evidence: `docs/evidence/policy.md` (58 focused tests).
- [x] Implement billing normalization/arithmetic and pure routing/escalation policy. Evidence: `docs/evidence/policy.md` (58 focused tests).
- [x] Turn the controlled cases into executable tests; add monetary normalization and schema-validation cases. Evidence: `docs/evidence/policy.md` (58 focused tests).
- [ ] Smoke-test the exact schema against the selected real model; record usage and any schema adjustments.

Gate: locked environment starts, policy/validation tests pass, exact model schema works on a real response. No unsupported claims of full application functionality.

## M2 — Working vertical slice

- [x] Persist incoming requests, attempts, accepted analyses and derived decisions with migrations. Offline verification: docs/evidence/m2-backend.md; real concurrency/queue acceptance pending.
- [x] Implement canonical webhook, principal-scoped idempotency, session/CSRF and bearer-token authentication. Offline verification: docs/evidence/m2-backend.md; real concurrency/queue acceptance pending.
- [x] Publish after commit, atomically claim tasks, call the model outside transactions, and persist result/completion atomically. Offline verification: docs/evidence/m2-backend.md; real concurrency/queue acceptance pending.
- [x] Implement status and export endpoints and safe error envelopes. Offline verification: docs/evidence/m2-backend.md; real concurrency/queue acceptance pending.
- [ ] Build visual tester that posts to the webhook and displays asynchronous progress/results.
- [ ] Preserve the five assessment inputs verbatim; sample loader uses the same intake service.
- [ ] Process all five inputs through the real container stack and model; save complete output records.

Gate: form submission automatically reaches a persisted/exportable result through Redis/Celery; all five records are real and complete.

## M3 — Reliability and review experience

- [ ] Add bounded retries, explicit timeouts, sanitized failures, cost tracking, and eligible manual retry.
- [ ] Protect concurrent duplicate ingestion/task deliveries and accepted results with meaningful tests.
- [ ] Verify publication-failure visibility and operator-assisted republication without resetting retry budgets.
- [ ] Test transient/permanent provider errors, invalid output/refusal, retry exhaustion, permissions and CSRF.
- [ ] Build inbox/detail and separate Human Review queue with original text, evidence and decision reasons.
- [ ] Test browser interaction and capture screenshots for tester, completed request, escalation and failure states.

Gate: core behavior and implemented recovery paths are verified in the real stack; simulated faults are labeled, and worker-crash recovery limits are documented.

## M4 — Evaluation and prompt optimization

- [ ] Define benchmark record format and metrics before generation; keep policy fixtures outside the 50-message count.
- [ ] Generate and review an initial small batch against the written rubric; resolve label ambiguities.
- [ ] Complete 50 cases: 5 supplied acceptance, 25 development, 10 validation, 10 locked final test. Keep related scenario families within one split.
- [ ] Validate scorer behavior with known good/bad predictions before live benchmarking.
- [ ] Run a baseline; score category/priority, entities, semantic signals, summaries and output validity separately.
- [ ] Record end-to-end destinations, missed/unnecessary escalations, incorrect automatic routing and automation coverage.
- [ ] Iterate versioned prompts on development cases; select candidates using validation. Record experiments, usage, latency and observed regressions.
- [ ] Freeze prompt/model/schema/policy; run locked final test once. Disclose any reuse after changes.
- [ ] Save predictions, run metadata and an honest report with counts/denominators, unknown costs and limitations.

Gate: reproducible results show measured behavior rather than asserted accuracy; required five outputs match the chosen final configuration.

## M5 — First complete submission checkpoint

- [ ] Finish tested clean-checkout setup and reviewer commands in README.
- [ ] Write prompt rationale and separate one-to-two-page architecture document.
- [ ] Record real AI-assisted development decisions, mistakes caught and corrections; no manufactured anecdotes.
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
