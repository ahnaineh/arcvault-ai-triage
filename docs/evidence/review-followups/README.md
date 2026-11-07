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
No accuracy claim is made. Priority, signals and complete policy expectations still
need independent freezing before this becomes a runnable benchmark dataset.

Remaining dependencies: independent human summary signoff; holdout label review
and complete benchmark-schema conversion; configuration/protocol freeze and safe
budget-accounted run commands. Do not run paid inference against this preliminary
holdout. Planned run size is eight cases for one configuration, or sixteen for a
paired V3/V4 comparison. A defensible dollar bound requires the configured input
bound and reservation accounting, which this follow-up does not yet establish.
