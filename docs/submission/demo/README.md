# ArcVault demo

[Watch the 2:15 AI-narrated demo](arcvault-demo.mp4) · [The five shown results](narrated-five-outputs.json)

We submit one fresh login request through the real webhook, PostgreSQL, Redis/Celery and Terra V4. We then review the other four results saved during our earlier live run. The narration identifies these saved results. Nothing is mocked.

The revised UI shows category, priority, confidence percentage, core issue, urgency, extracted identifiers, destination, Human Review status and summary. Source excerpts, billing assumptions and technical history expand when needed. The invoice shows a $260 apparent difference; the outage goes to Human Review.

## Recording

The video uses an AI-generated Cedar voice from OpenAI, with natural narration and no subtitles. This edit reuses the recorded live submission and four saved outputs; it makes no additional triage calls. The policy and export scenes were recorded again using the documented admin / admin demo login. Cuts and held frames give time to read the results. Source outputs are unchanged.

[Script](script.json) · [Scene timings](timeline.json) · [Runtime file hashes](runtime-hashes.json) · [Manifest](manifest.json)

Checks: desktop/mobile and keyboard interaction; all required fields; fresh request completion and persisted export; full H.264/AAC decode; readable frames; audio transcription matching the intended narration. Audio peaks remain below zero dBFS. The UI passed 178 tests, Ruff and three JavaScript harnesses; see [UI evidence](../../evidence/ui-redesign.md).

## Earlier live run

All five original inputs completed in the earlier queued run. One transient failure retried successfully without a duplicate request. Its unknown usage reservation remains retained. [Original five outputs](live-assessment-outputs.json), [startup log](startup.log), and [original recording](https://github.com/ahnaineh/arcvault-ai-triage/blob/fec54753d0696eaa4b510ea3f7ee736983d2ddbd/docs/submission/demo/arcvault-demo.mp4) remain available.


Speech API reference: [OpenAI text-to-speech documentation](https://developers.openai.com/api/docs/guides/text-to-speech).
