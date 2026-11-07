# Requirements and outputs

| Required step | Implementation | Evidence |
| --- | --- | --- |
| Automatic ingestion | Webhook saves and queues each new message | [Demo](demo/README.md) |
| LLM classification | Category, priority, and confidence | [Five JSON records](demo/narrated-five-outputs.json) |
| Enrichment | Core issue, entities, urgency, and outage signal | Each record's `analysis` |
| Routing | Four standard teams and Human Review fallback | [Routing rules](ARCHITECTURE.md#routing-and-escalation) |
| Persistent output | PostgreSQL record and JSON export with a two-sentence summary | Each record's `summary` and `decision` |
| Human escalation | Low confidence or defined escalation criteria | Outage result and [policy tests](../../tests/test_policy.py) |

## The five supplied messages

| Message | Category | Priority | Destination |
| --- | --- | --- | --- |
| Login returns 403 | Bug Report | High | Engineering |
| Bulk audit-log export | Feature Request | Low | Product |
| Invoice #8821 discrepancy | Billing Issue | Medium | Billing |
| Okta SSO setup | Technical Question | Medium | Technical Support |
| Dashboard unavailable to multiple users | Incident/Outage | High | Human Review |

Priority and the outage signal express urgency inferred from impact. The separate `urgency` field records explicit urgency, such as a deadline. It is Unknown for these five messages. The outage still has High priority and triggers Human Review.

The invoice's apparent difference is $260. Its record states the currency and monthly-charge assumptions. Confidence below 0.70 triggers review; exactly 0.70 does not. The billing threshold is strictly greater than $500.

## Reading a JSON record

| Section | Contents |
| --- | --- |
| `request` | Original message, source, ID, and receipt time |
| `analysis` | Model classification, entities, signals, and summary sentences |
| `decision` | Standard team, final destination, escalation reasons, and billing calculation |
| `summary` | Readable summary for the receiving team |
| `provenance` | Model and prompt/schema/policy versions |
| `processing` | Attempts, latency, and token usage |
| `review` | Null; human correction actions are not implemented |

All five summaries were checked against their source messages by an implementation assistant. Each has two sentences and preserves the customer's request without inventing a diagnosis or promise. Independent human scoring of summary quality remains pending.
