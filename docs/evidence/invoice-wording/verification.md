Invoice wording policy verification

Base: 5d7f72b98c18678c8a87e1b903acef8c74d4ab9d. Offline only.

The direct invoice exception assumes one monthly charge and equal components when both components are unspecified, the expected period is monthly, and the billed period is unspecified or invoice. USD currency normalization remains required. Assumptions are emitted once each.

Supported source grammar retains the complete invoice-versus-contract statement with optional terminal period and normalized whitespace. Optional closing forms are: “Can/Could someone/you [please] look into this”, “Can/Could you [please] check this/investigate/help”, and “Please check this/investigate”. Each accepts a period, question mark, or absent terminal punctuation, including trailing whitespace. Full-source matching rejects extra clauses. Exact evidence must still occur in the original source.

This only partially mitigates #24: other neutral phrasings remain unresolved; no general natural-language invariance is claimed. Schemas, prompts, historical inference artifacts, and docs/submission are unchanged.

Validation: 283 offline tests passed with six existing staticfiles warnings; Ruff, Django system check, and migration drift check passed. Tests use an existing Python 3.14 environment and SQLite with an offline test secret. Coverage includes natural imperatives, polite questions, punctuation/whitespace variation, and appended period/currency/component conflicts remaining Human Review/null. No paid calls. Submission subtree SHA: 8882c55e51d9a7f9d161a39c0c038d16f5267d93 (identical to base).
