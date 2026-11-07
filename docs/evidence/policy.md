# Policy regression evidence

Command (November 7, 2026):

```sh
UV_CACHE_DIR=/tmp/arcvault-uv uv run --no-project --with pydantic --with pytest python -m pytest -q tests/test_policy.py
```

58 passed. Includes 25 controlled fixtures and composed validation → billing → policy regressions for absent/unsupported monetary evidence, comma/currency numeric support, unknown/unrecognized/incompatible bases, nested mutation, copied NaN, and independent export dictionaries.

Populated monetary facts require exact excerpts; normalized decimal occurrence is mechanically checked. Occurrence does not establish contextual semantics or correct billed/expected attribution. Those require later evaluation.

Canonical periods: invoice, monthly, annual, one_time. Canonical components: subscription, total, usage, tax. Other wording is retained but unresolved. Matching components required; invoice/monthly uses the documented single-charge synthetic assumption.

Accepted analyses are mutable working models, but any change invalidates policy acceptance. validate_analysis records an independent snapshot; decide rejects changed or bypass-constructed instances and revalidates structure. Export dictionaries and returned decisions are independent serialization values; editing them cannot edit accepted analysis or another decision. This is an application integrity contract, not protection against hostile Python code modifying private attributes.

No live API calls, provider schema acceptance, runtime/container integration, or full application acceptance claimed. Single model call architecture unchanged.

## Independent integration review

Remote functional head verified: `7a7ac6db7c4f3cdf3887bee8b2c86210eba64ef8`. Independent reviewer reported no blockers and 58 passing tests using the command above. Probes verified $1240 versus $980/month yields $260 Billing; exact 500 automatic/500.01 review; signed undercharge; confidence .699999 review/.70 automatic; monetary evidence normalization; rejection of unsupported evidence, Unknown basis, mutated and bypass models. Integration rerun: 58 passed in 0.08s. Documentation-only integration. Semantic attribution, live provider and runtime integration remain pending.
