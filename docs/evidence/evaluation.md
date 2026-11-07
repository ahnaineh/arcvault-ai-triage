# M4 offline foundation evidence

Executed 2026-11-07:

```
python3 -m unittest discover -s tests -p 'test_eval*.py' -v
# 4 tests passed; includes known-good, deliberately wrong dimensions,
# missing coverage, duplicate predictions, family leakage and missed escalation.
python3 -m evals.score validate
# 50 draft cases validated
```

No provider calls, costs, latency measurements, prompt iteration or benchmark runs occurred.

Dataset: `evals/dataset.json`, 5 exact attachment inputs, 25 development,
10 validation, 10 test. All labels await independent review, including the
candidate rubric applied to assessment inputs. The generator is not an independent
reviewer. Assessment text is sourced from the authorized assessment attachment.
Policy fixtures are excluded. Scenario-family IDs cannot cross splits.
Generated cases currently repeat narrow templates; different split-specific
family IDs do not prove semantic independence. Independent review must expand
families and audit near duplicates before any live benchmark. This is a draft,
not a reviewed benchmark. Test text has been generated/inspected for harness
construction, never used for prompt iteration; freeze configuration before
unlocking it and disclose any subsequent reuse.

CLI:

```
python3 -m evals.score score predictions.json --split development
python3 -m evals.score score predictions.json --split test --unlock-test
```

Prediction file is a JSON array of `{id, analysis, decision, cost_usd?, latency_ms?}`.
`analysis` follows the checked-in schema; `decision` contains exactly the four
expected policy keys. Pass actual pipeline decisions; the harness never substitutes
expected semantic fields or recomputes runtime policy. Extra decision metadata
must be removed by an explicit export adapter before scoring. Unknown and duplicate
IDs fail. Missing predictions remain in the selected split denominator.

Separate counts/denominators cover category, priority, required entity recall,
signals, structural schema, lexical summary constraints and exact routing.
Missed and unnecessary escalations and incorrect automatic destinations use the
whole selected split denominator; automatic coverage counts structurally valid
responses explicitly routed without review. Prediction coverage is separate.
Cost and latency are caller-supplied raw inputs, null when absent, never inferred.

Limitations: schema checks implement only keywords used in the current schema,
not application semantic evidence/money validation. Entity checking is required
recall, not precision. Summary required facts currently use full source text as a
conservative lexical proxy, so faithful paraphrases may fail. Forbidden phrases
are illustrative, not exhaustive. Neither lexical success nor schema validity
proves factual faithfulness. Every summary still requires independent manual
review for required facts, unsupported claims, attribution and omissions; the
report always marks that review pending. No aggregate quality claim is justified
by harness unit tests. Billing normalization, confidence boundaries, malicious
instructions, ambiguity and broader urgency coverage remain dataset expansion
work for independent review. No unintegrated policy-agent files were consumed.
