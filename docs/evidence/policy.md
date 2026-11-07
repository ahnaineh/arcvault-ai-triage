# M1 validation and policy evidence

Executed November 7, 2026:

```
UV_CACHE_DIR=/tmp/arcvault-uv uv run --no-project --with pydantic --with pytest python -m pytest -q tests/test_policy.py
49 passed in 0.07s
```

Initial download required network escalation. Initial execution: 48 passed, one test incorrectly required a USD assumption for EUR; corrected that expectation and reran successfully.

API: `validate_analysis(payload, message)` returns strict Pydantic v2 `Analysis`; direct validation requires message context. `decide(analysis)` independently normalizes billing and returns export decision fields. `decide_projection` supports controlled fixtures, not unvalidated model output ingestion.

Billing basis ambiguity resolved conservatively: exact matching known period/component tokens only; invoice/monthly exception requires known matching components and records an assumption. Missing components remain unresolved. USD/US$/$ accepted; no FX or inferred currency. Decimal precision accommodates all input digits; signed undercharges retained. No schema changes.

Coverage: all 25 frozen policy fixtures, eight invalid shapes/numbers, seven invalid monetary formats, exact contextual and mandatory outage evidence, eight billing/composition cases. Exact excerpts establish occurrence, not semantic correctness. Summary grounding and sentence semantics require later evaluation. No provider compatibility, live inference, runtime stack, or end-to-end claims. Dependencies executed in an isolated temporary uv environment; dependency files untouched.
