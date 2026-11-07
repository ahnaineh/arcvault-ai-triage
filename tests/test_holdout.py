import copy
import json
from pathlib import Path

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.triage.management.commands.run_holdout import validate

DATA = Path('evals/fresh_holdout.json')
CONFIG = 'docs/evidence/review-followups/holdout.example.json'


def test_valid_holdout():
    validate(json.loads(DATA.read_text()))


@pytest.mark.parametrize('mutation', ['category', 'queue', 'currency', 'outage', 'missing'])
def test_reject_invalid_labels(mutation):
    cases = copy.deepcopy(json.loads(DATA.read_text()))
    if mutation == 'category':
        cases[0]['acceptable_categories'] = ['General Inquiry']
    elif mutation == 'queue':
        cases[0]['expected_policy']['standard_destination'] = 'Customer Support'
    elif mutation == 'currency':
        cases[3]['expected_policy'].update(final_destination='Billing', human_escalation=False)
    elif mutation == 'outage':
        cases[4]['acceptable_categories'] = ['Bug Report']
    else:
        del cases[0]['expected_policy']['escalation_reasons']
    with pytest.raises(ValueError):
        validate(cases)


def test_dry_run_never_builds_client_and_freezes(tmp_path, monkeypatch):
    import openai
    def forbidden(*args, **kwargs):
        raise AssertionError('client constructed')
    monkeypatch.setattr(openai, 'OpenAI', forbidden)
    call_command('run_holdout', dataset=str(DATA), config=CONFIG, run_dir=str(tmp_path))
    config = json.loads(Path(CONFIG).read_text())
    config['budget'] = '84'
    changed = tmp_path / 'config.json'
    changed.write_text(json.dumps(config))
    with pytest.raises(CommandError, match='identity'):
        call_command('run_holdout', dataset=str(DATA), config=str(changed), run_dir=str(tmp_path))


def test_illustrative_cannot_execute(tmp_path):
    with pytest.raises(CommandError, match='Illustrative'):
        call_command('run_holdout', dataset=str(DATA), config=CONFIG, run_dir=str(tmp_path), execute=True)


def test_right_now_is_not_semantic_truth():
    cases = json.loads(DATA.read_text())
    cases[0]['message'] += ' I am reading the instructions right now.'
    validate(cases)


@pytest.mark.parametrize('field,value', [
    ('billing_status', 'unknown'), ('reported_overcharge', True),
    ('source', 'Chat'), ('message', ' '),
    ('expected_signals', {'active_service_outage': 'yes'}),
])
def test_invalid_annotations(field, value):
    cases = json.loads(DATA.read_text())
    cases[0][field] = value
    with pytest.raises((ValueError, TypeError)):
        validate(cases)


def test_duplicate_normalized_message():
    cases = json.loads(DATA.read_text())
    cases[1]['message'] = '  ' + cases[0]['message'].upper()
    with pytest.raises(ValueError, match='duplicate'):
        validate(cases)


def test_execute_exports_failed_case_in_denominator(tmp_path, monkeypatch):
    # Bypass only filesystem location checks, retaining all runner accounting.
    import os
    from unittest.mock import Mock

    from apps.triage.providers.openai_provider import ProviderError, ProviderResult
    from apps.triage.schemas import validate_analysis
    monkeypatch.setattr(Path, 'resolve', lambda self: self)
    directory = Path(os.path.relpath(tmp_path))
    config = json.loads(Path(CONFIG).read_text())
    config.update(illustrative=False, budget='200', project_budget='200',
                  reconciled_history={'evidence': 'offline fixture',
                                      'known_cost': '0', 'unknown_reservation': '0'})
    config_path = tmp_path / 'execute.json'
    config_path.write_text(json.dumps(config))
    cases = json.loads(DATA.read_text())
    data = {'category': 'Technical Question', 'priority': 'Low', 'confidence': .9,
            'core_issue': 'Question', 'entities': [],
            'urgency': {'level': 'Unknown', 'evidence': []},
            'signals': {k: {'value': False, 'evidence': []}
                        for k in cases[0]['expected_signals']},
            'billing_comparison': None, 'summary_sentences': ['One.', 'Two.']}
    calls = []
    provider = Mock(enforces_bounds=True)
    provider.inference_identity.return_value = None

    def invoke(message, cfg):
        calls.append(message)
        if len(calls) == 2:
            raise ProviderError('offline terminal')
        return ProviderResult(validate_analysis(data, message), message,
                              'mock', 'v1', '1', 'hash', 'hash', 0, None)

    provider.side_effect = invoke
    monkeypatch.setenv('OPENAI_API_KEY', 'offline')
    monkeypatch.setattr('openai.OpenAI', Mock())
    monkeypatch.setattr('apps.triage.management.commands.run_holdout.BoundedOpenAIAdapter',
                        lambda **kwargs: provider)
    call_command('run_holdout', dataset=str(DATA), config=str(config_path),
                 run_dir=str(directory), execute=True)
    result = json.loads((directory / 'holdout.score.json').read_text())
    assert result['cases'] == result['predictions'] == 8
    assert result['metrics']['operational_failures'] == {'count': 1, 'denominator': 8}
    assert result['metrics']['completed']['count'] == 7
    assert all(r['manual_summary_review'] == 'review_needed' for r in result['rows'])
    assert calls == [c['message'] for c in cases]
    assert (directory / 'holdout.exports.json').exists()
    assert (directory / 'holdout.predictions.json').exists()
