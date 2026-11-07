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
