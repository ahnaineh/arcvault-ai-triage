# UI redesign

The inbox, tester and request detail share one restrained teal/ink style. The result leads with destination, category and priority. Confidence is displayed as a percentage without rounding across the 70% threshold. Core issue, urgency, escalation status, summary and extracted identifiers remain visible. Evidence, billing assumptions and technical metadata expand on demand. No raw dictionaries are shown.

## Assessment field check

- Classification: category, priority and confidence percentage in the main result.
- Enrichment: core issue, identifiers and urgency in the main result; source excerpts expand beside identifiers.
- Routing: final destination, explicit Human review status and reasons. Escalations retain their standard destination.
- Output: summary, original message and Export JSON. Exported records are unchanged.

Screenshots: [desktop invoice](ui-redesign/invoice.png), [mobile invoice](ui-redesign/invoice-mobile.png), [outage](ui-redesign/outage.png), [inbox](ui-redesign/inbox.png), [tester](ui-redesign/tester.png).

## Verification

178 Python tests, Ruff and all three existing JavaScript harnesses passed. After the final percentage/amount formatting adjustments, the focused UI tests and Ruff passed again. Warnings concerned absent local staticfiles and the sandbox's read-only pytest cache.

Real Chrome at 1440×1000 and 390×844: login, saved results, no document overflow, no page errors, and keyboard Enter opening/closing Technical details passed. No new inference was used for these checks. The existing persisted exports remain unchanged.

Browser navigation exposed a single synchronous Gunicorn worker waiting on an idle connection. The Docker default now uses four threads; the demo runs the identical command. With one idle socket held open, the health request completed in 0.03 seconds. Login and navigation then passed. The final presentation files were copied into the owned demo container and static assets recollected after its successful image rebuild; this is not a claim of a second pristine image build.
