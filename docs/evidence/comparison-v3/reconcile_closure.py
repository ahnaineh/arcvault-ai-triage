"""Offline audit only: no provider client, mutation of raw evidence, or paid calls."""
import hashlib
import json
from decimal import Decimal
from pathlib import Path

from apps.triage.acceptance import accounted
from apps.triage.policy import decide
from apps.triage.schemas import validate_analysis
from evals.export_adapter import adapt

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'docs/evidence'


def read(path):
    return json.loads(path.read_text())


def journal(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def reconcile():
    cases = read(ROOT / 'evals/dataset.json')
    by_case = {c['id']: c for c in cases}
    reports = read(BASE / 'comparison-v3/results.json')
    models = {}
    combined = Decimal('19.01065694')
    for model in ('gpt-6-luna', 'gpt-6.1-terra'):
        directory = BASE / 'comparison-v3' / model
        events = journal(directory / 'events.jsonl')
        config = read(directory / 'config.json')
        reserved = {e['request_id']: e for e in events if e['state'] == 'reserved'}
        raw = {e['request_id']: e['payload'] for e in events if e['state'] == 'raw_response'}
        terminals = {e['request_id']: e['result'] for e in events if e['state'] == 'completed'}
        failed = {e['request_id'] for e in events if e['state'] == 'failed'}
        exports = read(directory / 'exports.json')
        predictions = read(directory / 'predictions.json')
        assert len(reserved) == len(raw) == len(terminals) == len(exports) == 50
        assert set(reserved) == set(raw) == set(terminals)
        assert adapt(exports, cases) == predictions
        for record in exports:
            rid = record['request']['id']
            case = by_case[reserved[rid]['sample_id']]
            assert record == terminals[rid]
            assert (record['request']['message'], record['request']['source']) == (case['message'], case['source'])
            payload = json.loads(raw[rid]['output_text'][0])
            assert raw[rid]['status'] == 'completed'
            assert record['processing']['attempts'][0]['usage'] == raw[rid]['usage']
            if rid in failed:
                assert record['analysis'] is None and record['error']
                try:
                    validate_analysis(payload, case['message'])
                except ValueError as exc:
                    assert 'evidence must be an exact message excerpt' in str(exc)
                else:
                    raise AssertionError('Failure lacks raw validation explanation')
            else:
                assert record['analysis'] == payload
                assert record['decision'] == decide(validate_analysis(payload, case['message']))
            usage = raw[rid]['usage']
            assert usage['total_tokens'] == usage['input_tokens'] + usage['output_tokens']
            assert 0 <= usage.get('reasoning_tokens', 0) <= usage['output_tokens']
        total, _ = accounted(events, config)
        report = reports['models'][model]
        assert total == Decimal(report['conservative_accounted_usd'])
        totals = {k: sum(p['usage'].get(k, 0) for p in raw.values()) for k in ('input_tokens', 'output_tokens', 'reasoning_tokens')}
        assert totals['input_tokens'] == report['input_tokens']
        assert totals['output_tokens'] == report['output_tokens_including_reasoning']
        assert totals['reasoning_tokens'] == report['reasoning_tokens']
        rates = (Decimal('.1'), Decimal('.5')) if model == 'gpt-6-luna' else (Decimal(1), Decimal(5))
        estimate = (rates[0]*totals['input_tokens'] + rates[1]*totals['output_tokens']) / 1000000
        assert estimate == Decimal(report['standard_price_estimate_usd'])
        maximum = (Decimal(config['input_price_per_million'])*config['input_token_bound'] + Decimal(config['output_price_per_million'])*config['output_token_cap'])/1000000
        failed_retained = sum(Decimal(reserved[r]['reservation']) for r in failed)
        assert failed_retained == maximum * len(failed)
        # Replay each durable journal prefix to check the ceiling BEFORE every call.
        prefix = []
        max_committed = Decimal(0)
        history = Decimal(config['reconciled_history']['known_cost']) + Decimal(config['reconciled_history']['unknown_reservation'])
        for event in events:
            prefix.append(event)
            committed = history + accounted(prefix, config)[0]
            max_committed = max(max_committed, committed)
            assert committed <= Decimal(83)
        combined += total
        models[model] = {'raw_to_terminal_to_export_to_prediction': 'exact', 'calls': 50,
            'accepted_raw_analyses_equal_exports': 50-len(failed), 'retained_rejected_raw_outputs': len(failed),
            'usage': totals, 'standard_price_estimate': str(estimate),
            'conservative_accounted': str(total), 'failed_maxima_retained': str(failed_retained),
            'maximum_prefix_accounted': str(max_committed)}
    assert combined == Decimal(reports['total_project_accounted_usd'])
    original = read(BASE / 'benchmark-20261107/reconciliation.json')
    assert hashlib.sha256((ROOT / original['source']).read_bytes()).hexdigest() == original['source_sha256']
    old = journal(ROOT / original['source'])
    usages = [e['usage'] for e in old if e['state'] == 'provider_returned']
    assert sum(u['input_tokens'] for u in usages) == 4738
    assert sum(u['output_tokens'] for u in usages) == 1026
    prior = read(BASE / 'benchmark-20261107/execution-summary.json')
    new_estimate = sum(Decimal(prior[p]['accounted_estimate_usd']) for p in ('baseline', 'development', 'validation', 'test', 'assessment'))
    assert new_estimate == Decimal('1.1007645')
    assert Decimal('6.22326144') + Decimal('11.617584') + Decimal('.069047') + new_estimate == Decimal('19.01065694')
    return {'models': models, 'historical_unknown_retained': '17.84084544',
        'prior_known_estimates': '1.1698115', 'total_accounted': str(combined),
        'ceiling': '83', 'actual_billed_cost': None,
        'scorer_aggregates': 'Reviewer independently verified exact equality; not recomputed by this audit',
        'summary_review': {'independent_human_review': 'pending', 'assistant_observations': 'prior narrative observations, not case-level authenticated adjudication', 'fabricated_review_labels': False}}


if __name__ == '__main__':
    print(json.dumps(reconcile(), indent=2))
