
### Application model selection (2026-11-07)

User-selected default: `gpt-6.1-terra`, replacing the prior planned GPT-4.1 mini default. Historical actual mini run records remain unchanged.

Official evidence: https://developers.openai.com/api/docs/models/gpt-6.1-terra lists Responses and Structured Outputs support, 1,050,000 context, 922,000 maximum input and 128,000 maximum output tokens. Reasoning supports none/low/medium(default)/high/xhigh/max. Adapter explicitly selects none with the existing 4096 output cap, and sends no sampling parameters.

https://developers.openai.com/api/docs/guides/structured-outputs documents strict JSON schema support and schema restrictions. Exact application schema server acceptance and account access remain UNVERIFIED; no model listing, secrets, or inference calls were used here.

https://developers.openai.com/api/docs/pricing lists Standard short context (<=272K input) rates per million: input $1, output $5, cached input $0.05, cache writes $1.25 (30m)/$2.50 (12h). Long context input $2/output $7.50. Regional processing +10%, Fast 2x. Future budget runner configuration must use these model-specific rates with conservative allowance for cache writes/tier, output <=128K, and verified input bounds. The runner has explicit prices rather than a model catalog; old mini rates must not be reused. Historical accounting and exact input-bound proof remain mandatory gates before execution.
