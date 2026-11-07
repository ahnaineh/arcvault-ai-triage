Invoice wording policy verification

Base: 5d7f72b98c18678c8a87e1b903acef8c74d4ab9d. Offline only.

The direct invoice exception assumes one monthly charge and equal components when both components are unspecified, the expected period is monthly, and the billed period is unspecified or invoice. USD currency normalization remains required. Assumptions are emitted once each.

Supported source grammar retains the complete invoice-versus-contract statement, with optional terminal period, arbitrary whitespace, and an optional neutral question: Can someone look into this, Could you please check this, Please check this, Please investigate, or Can you help. Other text remains unresolved; this is deliberately a bounded grammar, not unrestricted natural-language understanding. Exact evidence must still occur in the original source.

Regression tests cover all supported closings, trailing/leading whitespace, unrelated invoice IDs and amounts, threshold escalation, and adversarial period/currency/component additions. Historical evidence and docs/submission are untouched.

Validation: 206 offline tests passed; Ruff passed; Django system check passed; migration drift check passed. Used an existing Python 3.14 environment because fresh uv dependency downloads stalled. Six existing missing-staticfiles warnings occurred. Submission subtree SHA: 8882c55e51d9a7f9d161a39c0c038d16f5267d93 (identical to base).
