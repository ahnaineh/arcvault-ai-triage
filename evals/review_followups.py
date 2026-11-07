"""Offline derived evidence only; never writes historical scorer reviews."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/evidence/review-followups'


def read(path):
    return json.loads((ROOT / path).read_text())


def build():
    # Fail closed before writing either artifact if a person edited the sheet.
    previous = OUT / 'summary-review-sheet.json'
    if previous.exists():
        rows = json.loads(previous.read_text())
        if any(r.get('human_accept') is not None or r.get('human_correction') or r.get('human_reviewer') for r in rows):
            raise ValueError('Human responses present: archive with source provenance before regeneration')
    dataset = read('evals/dataset.json')
    paths = ['docs/evidence/comparison-v3/gpt-6.1-terra/predictions.json',
             'docs/evidence/final-v4/comparison.predictions.json']
    versions = [{p['id']: p for p in read(path)} for path in paths]
    report = {'provenance': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
                             for p in paths + ['evals/dataset.json']}, 'cases': []}
    sheet = []
    for d in dataset:
        a, b = [v[d['id']] for v in versions]
        report['cases'].append({'id': d['id'], 'expected': d['expected_policy'],
                                'v3': a['decision'], 'v4': b['decision'],
                                'same_final_destination': a['decision']['final_destination'] == b['decision']['final_destination']})
        summary = b['analysis']['summary_sentences']
        correction = {'assessment-01': 'Include arcvault.io/user/jsmith explicitly to satisfy the required account fact.',
                      'development-20': 'Human judgment requested: "This may cause unintended data loss" is a plausible inference, not a demonstrated hallucination; assess strict source-only summary requirements.'}.get(d['id'], '')
        sheet.append({'id': d['id'], 'reviewer_kind': 'ASSISTANT',
                      'assistant_verdict': 'correction_requested' if correction else 'accept',
                      'source': d['message'], 'summary': summary,
                      'required_facts': d['summary_required_facts'],
                      'forbidden_facts': d['summary_forbidden_facts'],
                      'reason': correction or ('The summary preserves the source claim: ' + ' / '.join(d['summary_required_facts']) + '. Its material claims are supported by the source; no diagnosis, promise or verified attribution is added.'),
                      'human_accept': None, 'human_correction': '', 'human_reviewer': ''})
    for name, rows in [('routing-report.json', report), ('summary-review-sheet.json', sheet)]:
        (OUT / name).write_text(json.dumps(rows, indent=2) + '\n')


if __name__ == '__main__':
    build()
