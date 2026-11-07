# Prompt integration and offline evidence closure

The earlier dry-run accounting fix did not fix acceptance prompt selection. At
7f4490d, application wiring explicitly selected V3 but the bounded adapter and
ArtifactIdentity defaulted to V1. That was a real integration mismatch, independent
of the measured model comparison. No paid calls were made for this closure.

One selector now resolves explicit prompt_version or OPENAI_PROMPT_VERSION (V3 by
default), validates V1/V2/V3 and loads the versioned artifact. OpenAIProvider,
BoundedOpenAIAdapter and ArtifactIdentity all use it. run_acceptance passes the
same config selection to execution and offline identity. run_benchmark defaults
to that selector and supports explicit --prompt-version or legacy --prompt path;
compare_models uses the selector too. Neither command mutates a constructed
provider's prompt. Explicit legacy V1 remains supported; no implicit V1 default
remains. Version/schema changes cannot reuse stale acceptance records in execution
or dry-run. Configuration changes also remain blocked by immutable runner config.

Tests inspect actual mocked SDK Responses instructions, not just version labels:
application and acceptance hashes agree for default V3 and explicit V1, journal
identities match the request, dry-run has zero pending after completion, completed
execution resume makes zero new API calls, and switching versions blocks reuse.
A separate command test verifies benchmark default V3 request/manifest/identity and
both execution/dry-run resume. Existing paired-command tests exercise identical
selected prompt on both models, no-duplicate resume and frozen-identity rejection.

V3 text is unchanged: SHA256
063c69ace6138f60d71d5385253bfd65313cd8f788e4735619af5f02934d8392,
4193 bytes/characters,543 whitespace-delimited words,8 lines. These are file-size
measurements, not tokenizer counts. No semantic optimization cycle, new model
calls or unmeasured quality claim accompanies this wiring fix. V1 hash remains
57fb1c068c867824a9e293c5274b674a41da6ab48481b6150d9384734e97d277.
Old evidence retains the prompt actually executed; none was relabeled to V3.
Frozen snapshots retain original code identities and require their original code
or an explicit audited harness amendment to resume after implementation changes.

## Raw evidence and arithmetic

Run `uv run python -m docs.evidence.comparison-v3.reconcile_closure` offline.
closure-reconciliation.json is its retained result. It verifies all50/model source
messages, raw-response-to-terminal-to-export equality, accepted analyses versus
raw JSON, policy decisions, adapter predictions, usage and reason-token arithmetic,
standard-price estimates, conservative accounting, every prefix's83 ceiling and
unchanged original-five raw-journal hash. Rejected raw analyses remain errors, not
repaired predictions.35 Luna and50 Terra accepted analyses match raw output exactly;
15 Luna raw outputs reproduce exact-excerpt validation failure.

Accounting decomposition:
- Historical uncertainty6.22326144 + uncertain connection11.617584 =17.84084544.
- Original-five conservative usage estimate.069047 + prior75-call estimate1.1007645
  =1.1698115 known estimates; subtotal19.01065694 including uncertainty.
- Luna conservative accounted19.5070458 includes15 retained full failed-call maxima
  totaling19.3875; these maxima are reservations, not token-derived cost estimates.
- Terra conservative accounted.8144950; project total39.33219774.
- Maximum replayed prefix51.27866524, below83. Actual billed cost remains unknown.
- Standard-price comparison estimates.0169297 Luna and.103802 Terra include all
  reasoning output tokens; they are distinct from conservative accounting.

User-supplied reviewer evidence independently recomputed scorer aggregates with
exact equality and verified Luna50 reservations/50raw/15failures/50terminal records,
plus57 focused checks. This closure reuses that evidence; it adds the raw-output
and accounting checks above instead of pretending to perform a fresh paid run.

## Summary status and limits

Prior reports contain assistant narrative observations about summary faithfulness.
Those are not an authenticated, case-level manual adjudication artifact. There is
no completed independent human review and no case-level summary_review labels were
invented. Independent human summary review remains PENDING; scorer fields remain
review_needed and summary_constraints/end_to_end_success remain zero for that
reason. The wiring and reconciliation audit does not upgrade that status.

Valid JSON, application-valid source evidence and correct category are different
properties. Luna's15 failures are exact-evidence violations, not proof of15 wrong
categories. Rubric/label conflicts, exact-entity span sensitivity, reused final set,
limited coverage, single stochastic sample/model/case and one missing Luna latency
remain material limits. Original holdout metrics stay separate and unchanged.

No new empty accounting root may be used to reset spend. Historical configs and
comparison-command history constants describe their original execution checkpoint;
a further authorized paid experiment must explicitly carry the current full ledger
forward. This closure makes no deployment, clean new holdout, independent manual
summary acceptance or additional paid execution claim.

Final combined verification after implementation:177 tests passed (six existing
missing-staticfiles warnings), Ruff clean, Django system check clean, migration
drift check reported no changes, git diff --check clean. All commands used explicit
SQLite/synthetic offline secret and writable /tmp UV cache/environment. No credentials
were read and no network model requests were made for this checkpoint.
