# ArcVault demo

[Watch the narrated demo](arcvault-demo.mp4) · [The five shown results](narrated-five-outputs.json)

We submit one fresh login request through the real webhook, PostgreSQL, Redis/Celery and Terra V4. We then review the other four results saved during our earlier live run. The narration identifies these saved results. Nothing is mocked.

The revised UI shows category, priority, confidence percentage, core issue, urgency, extracted identifiers, destination, Human Review status and summary. Source excerpts, billing assumptions and technical history expand when needed. The invoice shows a $260 apparent difference; the outage goes to Human Review.

## Recording

The video has an AI-generated Cedar voice from OpenAI, disclosed in the introduction. There are no subtitles. We recorded each scene in the real application, joined the scenes and synchronized the narration at a measured pace. The account-evidence scene was recaptured without inference to improve timing. Source outputs were not edited.

[Script](script.json) · [Scene timings](timeline.json) · [Runtime file hashes](runtime-hashes.json) · [Manifest](manifest.json)

Checks: desktop/mobile and keyboard interaction; all required fields; fresh request completion and persisted export; full H.264/AAC decode; readable frames; audio transcription matching the intended narration. Audio peaks remain below zero dBFS. The UI passed 178 tests, Ruff and three JavaScript harnesses; see [UI evidence](../../evidence/ui-redesign.md).

## Earlier live run

All five original inputs completed in the earlier queued run. One transient failure retried successfully without a duplicate request. Its unknown usage reservation remains retained. [Original five outputs](live-assessment-outputs.json), [startup log](startup.log), and [original recording](https://github.com/ahnaineh/arcvault-ai-triage/blob/fec54753d0696eaa4b510ea3f7ee736983d2ddbd/docs/submission/demo/arcvault-demo.mp4) remain available.

Conservative accounting is $52.69598874 of $83, including retained uncertainties and a $1 provisional allowance for speech generation and audio verification. This allowance is not a provider-enforced cap or a billing receipt. Actual billing remains unknown. No credentials, sessions or SQL backups are included.

Speech API reference: [OpenAI text-to-speech documentation](https://developers.openai.com/api/docs/guides/text-to-speech).
