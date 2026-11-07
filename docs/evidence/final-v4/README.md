# Final compact-prompt Terra benchmark

User requested one final run and no further prompt tuning. Default: `triage_v4`, 277 words, Terra with reasoning `none`, output cap 4096. V1–V3 and prior evidence remain unchanged.

50 reused cases completed once, zero retries and zero validation failures. This is comparison evidence, not a fresh holdout. Categories 47/50, priorities 40/50, exact entities 44/50, semantic signals 47/50, full routing decision equality 41/50. Previous V3: 49, 39, 44, 49, 44 respectively. This is a compactness/quality tradeoff, not a demonstrated overall accuracy improvement. No further tuning or label changes followed this run.

Zero missed escalations among 23 expected-review cases; four unnecessary escalations; zero wrong automatic destinations among 23 automatic records. Full routing equality also includes reasons and derived fields, so it is stricter than destination equality. Summary acceptance is unadjudicated: scorer summary/end-to-end values of zero represent the missing manual gate, not proof of 50 hallucinated summaries.

## Five required outputs

`assessment_outputs.json` contains the actual final five records: category, priority, signals and routing match 5/5; invoice apparent difference260 with disclosed synthetic assumptions; outage Human Review. Exact entity-set match is only1/5: additional/ differently bounded source-supported entities remain mismatches under the unchanged strict scorer. Do not claim a perfect assessment-output score.

Assistant source review of these five summaries: login accurately attributes403/update chronology; export describes requested capability and claimed savings; invoice preserves1240/980monthly and investigation request; Okta preserves setup/evaluation intent; dashboard attributes multiple-user failure and customer claim about provider fault. No invented diagnosis or promise observed. This is assistant review, not independent human adjudication. Okta extraction includes genericSSO as a product/integration, a specificity limitation. Full50 independent summary review remains pending.

## Provenance

The run used 47,242 input and 8,448 output tokens. See the [benchmark overview](../../submission/BENCHMARKS.md) for the comparison tables.

The original manifest identifies execution commitb1ec558 and hashes of actual prompt/schema/code. Test-only integration happened during execution; production benchmark code was fixed afterward for a separate multi-phase accounting issue. Original manifest and raw journal are preserved, not rewritten to imply execution of later code. Exact raw-to-analysis/export/prediction/scorer equality was verified offline. Configuration and journals include no API key.

Reproduce a NEW authorized run with `python manage.py run_benchmark --run-dir .acceptance-runtime/NEW-RUN --config config/acceptance/terra-v4-final.json --phase comparison --execute`; first reconcile all intervening spend into a new immutable config. Do not reuse this historical config as the current cumulative budget. Dry-run omits `--execute`. Never overwrite old manifests to bypass identity checks.

## Final offline checks

Combined consolidated suite177 passed, Ruff passed, Django check passed; six existing missing-staticfiles warnings. Prompt selection tests exercise explicit legacy versions, application/SDK/journal equality, dry-run/resume and version-change rejection. Cross-phase benchmark regression now runs V1 baseline then V2 development under one unchanged accounting ledger. No further inference required for that fix.
