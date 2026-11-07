# Application model

The application uses `gpt-6.1-terra`, reasoning `none`, a 4,096-token output limit and prompt `triage_v4`. The user selected Terra; it was retained after a paired comparison with Luna. Classification, extraction, urgency and summary come from one structured model request per attempt. Python owns routing and arithmetic.

Account access and strict-schema acceptance were demonstrated by real calls. The [final benchmark](evidence/final-v4/README.md), [paired comparison](evidence/comparison-v3/README.md) and [live queued demo](submission/demo/README.md) retain results and limitations. The comparison reused cases and does not establish unseen-case accuracy.

API billing is separate from the conservative usage estimates and retained uncertainty reservations in the evidence. Check current provider pricing before another paid run. Historical prompts, reports and model records remain available for reproduction.
