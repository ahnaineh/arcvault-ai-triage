"""Offline derivation only: never imports a provider or accesses credentials."""
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

from apps.triage.export import build_record
from apps.triage.schemas import validate_analysis

ROOT = Path('docs/evidence/terra-network-20261107')
original = ROOT / 'assessment_outputs.json'
records = json.loads(original.read_text())
events = [json.loads(line) for line in (ROOT / 'events.jsonl').read_text().splitlines()]
raw = [event['payload'] for event in events if event['state'] == 'raw_response']
assert len(raw) == len(records) == 5
derived = []
for record, response in zip(records, raw, strict=True):
    assert json.loads(''.join(response['output_text'])) == record['analysis']
    analysis = validate_analysis(record['analysis'], record['request']['message'])
    provenance = record['provenance']
    result = build_record(
        request=record['request'], analysis=analysis,
        output=SimpleNamespace(**{key: provenance[key] for key in ('model', 'prompt_version', 'schema_version')}),
        completed_at=provenance['completed_at'], attempt_id=provenance['accepted_attempt_id'],
        attempts=record['processing']['attempts'])
    result['provenance']['offline_derivation'] = {
        'original_sha256': hashlib.sha256(original.read_bytes()).hexdigest(),
        'kind': 'offline policy reprocessing; original model completion retained',
        'code_sha256': {str(path): hashlib.sha256(path.read_bytes()).hexdigest()
                        for path in map(Path, ['apps/triage/policy.py', 'apps/triage/schemas.py', 'apps/triage/export.py'])}}
    assert result['analysis'] == record['analysis']
    derived.append(result)
(ROOT / 'assessment_outputs.policy-1.1.json').write_text(json.dumps(derived, indent=2) + '\n')
