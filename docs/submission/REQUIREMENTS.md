# Requirement and evidence traceability

The assessment requires an urgency signal **based on message content**. V4's
`analysis.urgency` specifically measures expressed urgency: all five authentic
records say Unknown because none states a deadline or asks for immediate action.
Unknown does not mean low operational urgency. `analysis.priority` is the
content-derived impact/urgency signal; `active_service_outage` adds an explicit
availability signal. Read these fields together in the saved JSON. No historical
prompt or output has been rewritten to change this distinction.

| Exact assessment input | Expressed urgency | Content-derived priority and interpretation | Destination |
|---|---|---|---|
| Login 403 / jsmith | Unknown | High: blocked login | Engineering |
| Bulk audit-log export | Unknown | Low: proposed efficiency improvement | Product |
| Invoice 8821 | Unknown | Medium: actionable charge discrepancy | Billing |
| Okta SSO | Unknown | Medium: integration evaluation | Technical Support |
| Dashboard / multiple users / 2pm EST | Unknown | High: current multi-user disruption; outage signal true | Human Review |

These are interpretations of the existing fields, not new inference or a new
urgency scale. Priority alone does not escalate. The invoice's apparent $260
comparison uses the dollar/monthly-component assumptions disclosed in its record.

## Six steps and deliverables

1. Automatic ingestion: authenticated webhook, browser tester and sample loader
   share persisted intake and queued processing (see architecture and demo).
2. Classification: all five [actual records](demo/narrated-five-outputs.json)
   contain category, priority and model confidence.
3. Enrichment: those records contain one-sentence core issues, identifiers with
   verbatim evidence, and the urgency interpretation above.
4. Routing: Engineering, Product, Billing, Technical Support and Human Review;
   deterministic policy preserves the normal destination on escalation.
5. Persistence: PostgreSQL results exported as five JSON records, each with a
   two-sentence summary. Exports preserve the original analysis and provenance.
6. Escalation: confidence strictly below 0.70 (0.70 itself does not trigger),
   outage and other defined safety criteria; see `tests/test_policy.py` and
   `docs/CONTRACTS.md`. The fifth actual record demonstrates outage escalation.

[Prompt and rationale](../prompts.md), [architecture](ARCHITECTURE.md), and
[recording with editing/provenance limits](demo/README.md) complete the package.
The current 2:15 recording shows one fresh login submission and four saved
results. The earlier queued run, not the final edit, exercised transient retry.

## Summary review and validation limits

Implementation-assistant review compared all five narrated summaries with the
exact source messages: each has two sentences, preserves the requested action,
and adds no diagnosis or verified provider fault. The outage summary attributes
the provider-fault belief to the customer. This is not independent human
adjudication; that remains pending, as do production acceptance and calibration.

CI run 42399000396 failed before creating any jobs/check runs. Its workflow had
an unquoted `sqlite:///:memory:` scalar, whose trailing colon is invalid YAML in
that position. Quoting it fixes that syntax defect. Local checks do not establish
a green hosted run; the PR's hosted checks must be inspected separately.
