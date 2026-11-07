import json
from unittest.mock import Mock

import pytest

from apps.triage.acceptance import Runner
from apps.triage.providers.openai_provider import ProviderResult
from apps.triage.schemas import validate_analysis


@pytest.fixture
def setup(tmp_path, monkeypatch):
    # Tests use pytest temporary storage; production directory policy tested separately.
    monkeypatch.setattr('apps.triage.acceptance.Path.resolve', lambda self: self)
    path = tmp_path.relative_to('/tmp')
    monkeypatch.chdir('/tmp')
    config = {'model': 'mock', 'official_price_source': 'offline fixture', 'input_token_bound': 100,
                  'output_token_cap': 100, 'input_price_per_million': '1', 'output_price_per_million': '2',
                  'budget': '1', 'reconciled_history': {'evidence': 'fixture only', 'known_cost': '0', 'unknown_reservation': '0'}}
    cases = [{'sample_id': i, 'message': str(i)} for i in range(5)]
    data = {'category': 'Technical Question', 'priority': 'Low', 'confidence': .9, 'core_issue': 'Question',
                'entities': [], 'urgency': {'level': 'Unknown', 'evidence': []},
                'signals': {k: {'value': False, 'evidence': []} for k in
                         ['active_service_outage', 'insufficient_information', 'conflicting_intents']},
                'billing_comparison': None, 'summary_sentences': ['One.', 'Two.']}
    provider = Mock(enforces_bounds=True)
    provider.side_effect = lambda message, cfg: ProviderResult(validate_analysis(data, message), message,
        'mock', 'v1', '1', 'hash', 'hash', 0, None)
    return Runner(path, config), cases, provider


def test_success_order_and_resume(setup):
    runner, cases, provider = setup
    records = runner.run(cases, provider, execute=True)
    assert [r['model'] for r in records] == [str(i) for i in range(5)]
    runner.run(cases, provider, execute=True)
    assert provider.call_count == 5
    assert all('reservation' in e for e in map(json.loads, runner.path.read_text().splitlines()) if e['state'] == 'reserved')


def test_crash_uncertain_blocks(setup):
    runner, cases, provider = setup
    provider.side_effect = KeyboardInterrupt
    with pytest.raises(KeyboardInterrupt):
        runner.run(cases, provider, execute=True)
    with pytest.raises(ValueError, match='Unresolved'):
        runner.run(cases, provider, execute=True)
    assert provider.call_count == 1


def test_export_failure_preserves_results(setup, monkeypatch):
    runner, cases, provider = setup
    output = runner.directory / 'assessment_outputs.json'
    output.write_text('old evidence')
    with monkeypatch.context() as patch:
        patch.setattr('apps.triage.acceptance.os.replace', Mock(side_effect=OSError))
        with pytest.raises(OSError):
            runner.run(cases, provider, execute=True)
    assert output.read_text() == 'old evidence'
    runner.run(cases, provider, execute=True)
    assert provider.call_count == 5


def test_failed_sample_no_export(setup):
    runner, cases, provider = setup
    provider.side_effect = RuntimeError('sensitive')
    with pytest.raises(RuntimeError):
        runner.run(cases, provider, execute=True)
    assert not (runner.directory / 'assessment_outputs.json').exists()
    assert 'sensitive' not in runner.path.read_text()


@pytest.mark.parametrize('change', [{'budget': '0'}, {'reconciled_history': None}])
def test_preflight(setup, change):
    runner, cases, provider = setup
    runner.config.update(change)
    with pytest.raises(ValueError):
        runner.run(cases, provider, execute=True)
    provider.assert_not_called()


def test_resume_rejects_changed_config(setup):
    runner, cases, provider = setup
    runner.run(cases, provider, execute=True)
    runner.config['budget'] = '2'
    with pytest.raises(ValueError, match='configuration mismatch'):
        runner.run(cases, provider, execute=True)
    assert provider.call_count == 5


def test_reservation_exists_before_call(setup):
    runner, cases, provider = setup
    original = provider.side_effect
    def invoke(message, config):
        events = [json.loads(line) for line in runner.path.read_text().splitlines()]
        assert events[-1]['state'] == 'reserved'
        return original(message, config)
    provider.side_effect = invoke
    runner.run(cases, provider, execute=True)
