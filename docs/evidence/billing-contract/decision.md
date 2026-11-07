# Billing generalization decision for issue #24

Reviewed base: `2a8d742576e34c05045d440a8a132e963bfd3bba`.
Disposition: design complete; runtime generalization deferred. Issue #24 remains open.
No prompt, schema, policy version, stored result, or historical artifact changed.
No inference was performed. No repository AGENTS.md was found.

## Why an offline patch is insufficient

`schemas.validate_analysis` explicitly establishes structure and exact excerpts,
not semantic truth. A Money record has amount, currency, period, components and
unstructured evidence. Numeric validation accepts any matching number in the
combined excerpts. It does not bind a number to a currency, billed/expected role,
period or component. An invoice identifier can supply the matching digits;
an excerpt containing both charges can validate crossed roles. Currency and
basis assertions have no semantic source validation.

`policy.normalize_billing` has two independent acceptance paths. Its full-message
regex restricts the implicit invoice/monthly assumption to one sentence form and
listed closings. Its ordinary explicit-basis path accepts matching model fields
without checking the full source for omitted contradictory clauses. Fixing only
the regex therefore cannot establish the requested contract. Exact excerpt
membership must remain mandatory, but is insufficient for either path.

There is no reliable lexical boundary between neutral prose and financial
assertions: a request for help can also assert a different currency or duration;
a distant sentence can refer back using pronouns, negation, corrections or
arithmetic. Ignoring suffixes, enumerating polite sentences, or rejecting a list
of financial keywords cannot prove absence of contradictory meaning. A local
parser could safely support a declared controlled input language, but cannot
claim arbitrary customer-source coverage. Unsupported inputs would still require
Human Review, including many harmless paraphrases.

## Semantic decision required before implementation

Approve a new model-visible financial assertion extraction contract with full
source coverage, and accept that semantic completeness remains a model judgment,
not a deterministic guarantee. If arbitrary-source safety is an absolute
requirement, automated comparison must stay unresolved pending human verification
or structured authoritative billing data. A second model judgment alone is not
proof of completeness. This decision belongs to the parent/product owner.

Proposed contract (design only):

- Extract every financial assertion with exact source spans and offsets, including
  conflicting, corrected, negated and uncertain claims. Record the relation
  between corrections and superseded claims rather than silently deleting them.
- Bind each monetary mention to amount token, currency token, role
  (billed/expected/other/unknown), invoice/account reference, period, quantity,
  component and assertion polarity. Each field needs its own support span or an
  explicit unknown. Repeated equal amounts remain distinct mentions.
- Represent comparison links explicitly. Distinguish invoice total from unit
  price, tax, usage, credits, deposits and unrelated invoices. Include all
  additional clauses affecting the linked comparison, with ambiguity flags.
- Separate neutral text classification from financial assertion extraction.
  Record coverage/uncertainty for the entire source; do not treat an empty list
  of extracted conflicts as deterministic proof that none exists.

Deterministic validation must verify offsets/excerpts, numeric token boundaries,
Decimal normalization, role-link consistency, supported currencies and bases,
complete required fields and absence of declared uncertainty/conflicts. Never
infer currency from a bare identifier or use FX. Keep the documented synthetic
unqualified-dollar-to-USD assumption explicit and deduplicated. Unknown currency,
mixed currencies, ambiguous reference, unsupported period, or differing components
means unresolved and Human Review; no reported overcharge.

Allow the invoice/monthly assumption only when the semantic contract identifies a
direct billed-invoice versus expected-monthly comparison of the same charge,
without competing period/component/currency assertions. State explicitly that it
assumes one monthly charge of the same component. It is an apparent difference,
not a verified refund entitlement. The supplied invoice can retain its $260
result under that assumption after revalidation; preserving that result must not
force acceptance of unsupported sources. Polite closing wording has no role in
this decision. Use exact Decimal subtraction and the existing strict >500 gate.

## Required validation specification

Build dedicated offline billing fixtures with independently authored expected
facts and decisions, generated amounts and identifiers, and no dependency on a
particular sample's numbers. For each accepted case assert difference,
assumptions and destination; for rejected cases assert null difference and Human
Review. Exercise both current acceptance paths when evaluating a replacement.

| Family | Required cases and oracle |
| --- | --- |
| Paraphrase invariance | Active/passive sentences, labeled fields, reversed expected/billed order, multiline layout, spacing, punctuation and novel neutral closings preserve linked facts and decision. |
| Numeric binding | Unrelated ticket/invoice IDs, dates, counts and additional monetary mentions cannot supply a missing charge; crossed amount/evidence roles and broad excerpts containing both values must not authorize the wrong subtraction. |
| Currency | Explicit USD, supported dollar aliases and the synthetic assumption; unsupported currency, currency attached to the other amount, and later currency corrections fail closed. |
| Basis | Same supported explicit periods/components succeed; annual versus monthly, multiple months, unit versus total, tax/usage/credit clauses and missing or unrelated basis support fail closed. |
| Full-source contradiction | Prefix, middle and suffix assertions, clauses embedded in help requests, indirect references, negation and corrections remain visible even if the old Money fields omit them. |
| Evidence integrity | Nonexact excerpts, forged offsets, changed accepted payloads and numeric substrings remain rejected. Whitespace normalization never rewrites evidence. |
| Arithmetic/routing | Equal/negative differences, fractional precision, very large decimals and values below/equal/above the escalation boundary retain exact results. |
| Provenance | Old exports stay immutable; new output identifies new schema/prompt/policy versions and cannot silently relabel historical inference. |

Offline fixtures test deterministic consumers; they cannot demonstrate that a
model extracts these facts reliably. Before release, freeze the new schema,
prompt and policy identities; run authorized fresh inference over held-out
paraphrases/adversarial omissions and the supplied inputs; inspect raw outputs,
measure false comparable decisions separately from conservative failures, and
retain failures in denominators. Budget, model and retry approval are prerequisites
for that later inference. No paid calls are authorized by this document.

## Integration plan

1. Decide controlled-language/human-verification versus model semantic coverage.
2. Freeze extraction schema and source-support rules before parallel edits.
3. Implement source bindings and fail-closed policy, including the explicit-basis
   path; bump exported policy version and extraction identities together.
4. Run the offline matrix and existing suite, then separately authorize fresh
   inference. Preserve original raw outputs and exports with their identities.
5. Close #24 only after paraphrase invariance and omitted-conflict cases meet the
   agreed semantic acceptance boundary. This document alone does not close it.

## Offline verification on this branch

- Focused policy/invoice/export tests: 183 passed.
- Full offline suite: 283 passed; six warnings about absent local staticfiles.
- Ruff, Django system checks and git diff whitespace checks passed.
- These results establish baseline compatibility, not implementation or semantic
  acceptance of the proposed extraction contract.
