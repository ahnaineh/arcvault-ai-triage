# ArcVault assessment

ArcVault accepts a customer message, uses an LLM to classify and enrich it, then applies Python rules to choose a team or Human Review. PostgreSQL stores the original message and the completed JSON record.

| Deliverable | Read or watch |
| --- | --- |
| Working workflow | [2:15 demo](demo/README.md) |
| Five required outputs | [JSON records](demo/narrated-five-outputs.json) |
| System design and tradeoffs | [Architecture](ARCHITECTURE.md) |
| LLM instructions and rationale | [Prompt documentation](../prompts.md) |

The outputs follow the assessment order: login error, bulk export request, invoice discrepancy, Okta SSO question, and dashboard outage.

To try the application, follow [the local setup](../../README.md#run-locally).

For more detail, see [how each requirement is met](REQUIREMENTS.md) and [evaluation results](BENCHMARKS.md).
