# Prompt and model

ArcVault uses one LLM step for classification, extraction, and summary generation.

| Setting | Value |
| --- | --- |
| Model | `gpt-6.1-terra` |
| Instructions | [Exact triage_v4 prompt](../prompts/triage_v4.txt) |
| Output format | [Strict JSON schema](../contracts/analysis.schema.json) |
| Reasoning | `none` |
| Output limit | 4,096 tokens |

## Why this prompt

The prompt separates instructions from customer text and treats embedded commands as data. It defines categories and priority rules, requires source excerpts, and asks for all model-owned fields in one response. Python handles routing and money arithmetic because those rules should be deterministic. Exact excerpts make claims easier to check, but do not prove their meaning. The compact prompt uses fewer input tokens than V3, with lower category and routing scores on the same cases. With more time, I would focus on summary faithfulness and entity specificity. See [the evaluation](submission/BENCHMARKS.md) for the model choice and tradeoffs.

## How the response is used

The application validates the response before applying policy. Missing facts stay null or empty; provider failures do not become low-confidence classifications. Summaries attribute customer claims and must not invent causes, fixes, or promises.

Priority measures impact. `urgency` measures explicitly expressed urgency. The outage signal captures current broad or multi-user disruption. Confidence reflects classification uncertainty; it is not calibrated certainty.

## What I corrected during development

Valid JSON alone was not enough: a model could add commentary to a field that required a verbatim excerpt. Context validation now checks excerpts against the message. Failed calls can also incur costs, so usage is retained when available and unknown usage is not counted as zero. These lessons shaped the validation and evaluation code.

The [provider implementation](../apps/triage/providers/openai_provider.py) records model, prompt and schema identities with each result. Earlier prompt versions remain available to reproduce the recorded experiments.
