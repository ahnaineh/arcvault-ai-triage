# Offline review follow-ups

These files derive from immutable historical evidence. No inference was invoked.
Run `python3 -m evals.review_followups` to regenerate the routing comparison and
assistant review sheet. SHA256 input fingerprints are embedded in the report.
Review all sheet entries independently and fill human_accept, human_correction,
and human_reviewer; do not copy assistant verdicts into the historical scorer gate.

The eight fresh inputs in evals/fresh_holdout.json are reserved, unrun, and separate
from the historical dataset. Their scenario families deliberately overlap existing
product behavior; fresh wording does not establish independent scenario coverage.
Labels are assistant authored and need independent validation before paid testing.
No accuracy claim is made. All eight now carry scorer fields, priorities, signals,
policy projections and entity expectations. They remain assistant-authored drafts,
not evaluated or independently frozen labels. The command freezes exact bytes for
reproducibility, not label correctness. Human review must approve the expectations
before live use; summary acceptance remains a separate manual scorer gate.

Reproduction commands after dependency setup (from repository root):

```bash
export DJANGO_SECRET_KEY=offline-holdout-review DATABASE_URL=sqlite:///:memory: PYTHONDONTWRITEBYTECODE=1
PY=python
$PY manage.py run_holdout --dataset evals/fresh_holdout.json --config docs/evidence/review-followups/holdout.example.json --run-dir /tmp/pr33-holdout-final
$PY -m pytest -p no:cacheprovider --basetemp=/tmp/pr33-tests-verified -q
ruff check --no-cache .
$PY manage.py check
$PY manage.py makemigrations --check --dry-run
```

Dry-run: eight pending, zero clients and zero requests. Historical configured
USD 11/million input and 16.5/million output, conservative 1,050,000 input and
4,096 output bounds reserve USD 11.617584/case, USD 92.940672 as the sum of eight worst-case reservations.
These are configured historical prices, not current prices or billed costs.
This is neither expected nor billed cost, nor necessarily the required budget.
Runner reserves sequentially and reconciles accepted usage. USD 83 cannot guarantee
worst-case completion but may suffice at actual usage; history reduces headroom.

`--execute` rejects the illustrative example. Live use needs a user-supplied config
with illustrative=false, reconciled historical known cost and unknown reservation,
provenance, a sufficient authorized budget, API credentials, and persistent run
storage outside /tmp. No live authorization is implied by this command. Existing
Runner accounting retains unresolved reservations and adapter input safety bounds.
Provider input includes only sample ID, source and message; labels never enter it.
Dataset, prompt, schema, policy and config hashes are frozen in holdout.identity.json;
changed artifacts require a new reviewed run directory. Preserve historical evidence
and existing human decisions; regenerate no historical records for this holdout.

Execution writes holdout.exports.json, holdout.predictions.json and holdout.score.json
in the supplied run directory; summary review remains missing until human adjudication.
Inspect with `python -m json.tool RUN_DIR/holdout.score.json`.
Verification reused the existing local t3-03ab79f0 environment without installation.
