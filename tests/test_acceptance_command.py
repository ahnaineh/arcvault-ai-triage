import json
from io import StringIO
from unittest.mock import Mock

import httpx2 as httpx
import openai
import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.triage.acceptance import Runner
from apps.triage.providers.openai_provider import ProviderError
from tests.test_openai_provider import envelope


@pytest.fixture
def command(tmp_path, monkeypatch):
    monkeypatch.setattr('apps.triage.acceptance.Path.resolve', lambda self: self)
    monkeypatch.chdir(tmp_path)
    config = json.loads((__import__('pathlib').Path(__file__).resolve().parents[1] /
                         'config/acceptance/terra.json').read_text())
    # Relative directory preserves production's prohibition on /tmp runtime paths.
    path = tmp_path / 'config.json'
    path.write_text(json.dumps(config))
    client = Mock()
    client.with_options.return_value = client
    factory = Mock(return_value=client)
    monkeypatch.setattr(openai, 'OpenAI', factory)
    monkeypatch.setenv('OPENAI_API_KEY', 'mock-only')
    def run(execute=True):
        args = ['--run-dir', 'runtime', '--config', str(path)]
        if execute:
            args.append('--execute')
        output = StringIO()
        call_command('run_acceptance', *args, stdout=output)
        return json.loads(output.getvalue())
    def events():
        return [json.loads(line) for line in (tmp_path / 'runtime/events.jsonl').read_text().splitlines()]
    return run, client, factory, path, events


def valid_response(index=0):
    data = {'category': 'Technical Question', 'priority': 'Low', 'confidence': .9,
            'core_issue': str(index), 'entities': [],
            'urgency': {'level': 'Unknown', 'evidence': []},
            'signals': {key: {'value': False, 'evidence': []} for key in
                        ['active_service_outage', 'insufficient_information', 'conflicting_intents']},
            'billing_comparison': None, 'summary_sentences': ['One.', 'Two.']}
    return envelope(model='gpt-6.1-terra', output=[{
        'id': 'msg', 'type': 'message', 'role': 'assistant', 'status': 'completed',
        'content': [{'type': 'output_text', 'text': json.dumps(data), 'annotations': []}]}],
        usage={'input_tokens': 10, 'output_tokens': 20, 'total_tokens': 30, 'input_tokens_details': {'cached_tokens': 0, 'cache_write_tokens': 0}, 'output_tokens_details': {'reasoning_tokens': 0}})


def test_dry_run_no_sdk(command):
    run, client, factory, _, _ = command
    run(False)
    factory.assert_not_called()
    client.responses.create.assert_not_called()


def test_execute_order_artifacts_resume(command):
    run, client, _, _, events = command
    client.responses.create.side_effect = [valid_response(i) for i in range(5)]
    run()
    output = json.loads(__import__('pathlib').Path('runtime/assessment_outputs.json').read_text())
    assert [item['analysis']['core_issue'] for item in output] == list(map(str, range(5)))
    from apps.intake.sample_data import samples
    for item, case in zip(output, samples(), strict=True):
        assert item['request']['message'] == case['message']
        assert item['request']['source'] == case['source']
        assert item['request']['id']
        assert item['request']['received_at']
        assert item['summary'] == 'One. Two.'
        assert item['analysis']['entities'] == []
        assert item['decision']['human_escalation'] is False
        assert item['decision']['escalation_reasons'] == []
        assert item['decision']['standard_destination'] == item['decision']['final_destination']
        assert item['provenance']['policy_version'] == '1.1'
        assert item['provenance']['prompt_version'] == 'triage_v1'
        assert item['processing']['attempts'][0]['usage']['total_tokens'] == 30
    assert len([e for e in events() if e['state'] == 'completed']) == 5
    run()
    assert client.responses.create.call_count == 5
    client.with_options.assert_called_with(max_retries=0, timeout=60)


@pytest.mark.parametrize('field,value', [('reconciled_history', {}), ('budget', '0'),
                                         ('model', 'other'), ('output_token_cap', 0)])
def test_reject_configuration(command, field, value):
    run, client, _, path, _ = command
    config = json.loads(path.read_text())
    config[field] = value
    path.write_text(json.dumps(config))
    with pytest.raises((ValueError, CommandError)):
        run()
    client.responses.create.assert_not_called()


@pytest.mark.parametrize('kind', ['http', 'incomplete', 'refusal', 'invalid', 'oversized'])
def test_failure_evidence_and_retained_reservation(command, kind):
    run, client, _, _, events = command
    response = valid_response()
    if kind == 'http':
        client.responses.create.side_effect = openai.InternalServerError(
            'secret must not persist', response=httpx.Response(500, request=httpx.Request('POST', 'https://example.test')),
            body={'usage': {'input_tokens': 12}, 'secret': 'secret must not persist'})
    else:
        if kind == 'incomplete':
            response.status = 'incomplete'
        elif kind == 'refusal':
            response = envelope(output=[{'id': 'm', 'type': 'message', 'role': 'assistant',
                'status': 'completed', 'content': [{'type': 'refusal', 'refusal': 'secret must not persist'}]}])
        elif kind == 'invalid':
            response.output[0].content[0].text = '{}'
        elif kind == 'oversized':
            response.output[0].content[0].text = 'x' * 1048577
        client.responses.create.return_value = response
    with pytest.raises(ProviderError):
        run()
    records = events()
    assert [e['state'] for e in records] == ['reserved', 'raw_response', 'failed']
    assert records[0]['reservation']
    assert 'secret must not persist' not in json.dumps(records)
    if kind == 'oversized':
        assert records[1]['payload']['truncated']
        assert records[2]['usage']['total_tokens'] == 30
    if kind == 'invalid':
        assert records[1]['payload']['output_text'] == ['{}']
    with pytest.raises(ValueError, match='Unresolved'):
        run()
    assert client.responses.create.call_count == 1


def test_response_write_failure_retains_usage(command, monkeypatch):
    run, client, _, _, events = command
    client.responses.create.return_value = valid_response()
    original = Runner.append
    def append(self, event):
        if event['state'] == 'raw_response':
            raise OSError('disk error')
        original(self, event)
    monkeypatch.setattr(Runner, 'append', append)
    with pytest.raises(OSError):
        run()
    assert events()[-1]['usage']['total_tokens'] == 30


def test_export_error_no_partial_rewrite(command, monkeypatch):
    run, client, _, _, events = command
    client.responses.create.side_effect = [valid_response(i) for i in range(5)]
    from pathlib import Path
    Path('runtime').mkdir()
    output = Path('runtime/assessment_outputs.json')
    output.write_text('previous export')
    with monkeypatch.context() as patch:
        patch.setattr('apps.triage.acceptance.os.replace', Mock(side_effect=OSError))
        with pytest.raises(OSError):
            run()
    assert output.read_text() == 'previous export'
    assert len([e for e in events() if e['state'] == 'completed']) == 5
    run()
    assert client.responses.create.call_count == 5


def test_metadata_allowlist_and_bounds():
    from apps.triage.providers.openai_provider import response_evidence, safe_usage
    response = valid_response()
    response.id = 'x' * 10000
    response.model = 'y' * 10000
    evidence = response_evidence(response)
    assert len(evidence['id']) == len(evidence['model']) == 256
    assert safe_usage({'input_tokens': 1, 'output_tokens': 10**20,
                       'secret': 'private'}) == {'input_tokens': 1}


def assessment_payloads():
    from apps.intake.sample_data import samples
    categories = ['Bug Report', 'Feature Request', 'Billing Issue',
                  'Technical Question', 'Incident/Outage']
    payloads = []
    for case, category in zip(samples(), categories, strict=True):
        data = json.loads(valid_response().output[0].content[0].text)
        data['category'] = category
        data['core_issue'] = case['message']
        data['entities'] = [{'type': 'other', 'value': case['source'],
                             'evidence': case['message']}]
        if category == 'Billing Issue':
            data['billing_comparison'] = {
                'billed': {'amount': '1240', 'currency': '$', 'period': 'invoice',
                           'components': 'subscription', 'evidence': ['$1,240']},
                'expected': {'amount': '980', 'currency': '$', 'period': 'monthly',
                             'components': 'subscription', 'evidence': ['$980/month']}}
        if category == 'Incident/Outage':
            data['signals']['active_service_outage'] = {
                'value': True, 'evidence': ['Multiple users affected.']}
        payloads.append(data)
    return payloads


def execute_assessment(command):
    from pathlib import Path
    run, client, _, _, _ = command
    responses = []
    for payload in assessment_payloads():
        response = valid_response()
        response.output[0].content[0].text = json.dumps(payload)
        responses.append(response)
    client.responses.create.side_effect = responses
    run()
    return json.loads(Path('runtime/assessment_outputs.json').read_text())


def test_command_assessment_billing_and_outage_regression(command):
    from apps.intake.sample_data import samples
    records = execute_assessment(command)
    assert len(records) == 5
    for record, case, payload in zip(records, samples(), assessment_payloads(), strict=True):
        assert record['request']['source'] == case['source']
        assert record['request']['message'] == case['message']
        assert record['request']['id'] and record['request']['received_at']
        assert record['analysis'] == payload
        assert record['summary'] == 'One. Two.'
        assert record['provenance']['model'] == 'gpt-6.1-terra'
        assert record['provenance']['prompt_version'] == 'triage_v1'
        assert record['provenance']['schema_version'] == '1.0'
        assert record['provenance']['policy_version'] == '1.1'
        assert record['provenance']['completed_at']
        assert record['provenance']['accepted_attempt_id']
    billing = records[2]['decision']
    assert billing['reported_overcharge'] == '260'
    assert billing['standard_destination'] == billing['final_destination'] == 'Billing'
    assert billing['human_escalation'] is False
    assert 'billing_overcharge' not in billing['escalation_reasons']
    assert billing['comparison_assumptions'] == [
        'Unqualified $ interpreted as USD in synthetic domain',
        'Unqualified $ interpreted as USD in synthetic domain',
        'Direct invoice/monthly contract comparison treated as one monthly charge']
    outage = records[4]['decision']
    assert outage['standard_destination'] == 'Engineering'
    assert outage['final_destination'] == 'Human Review'
    assert outage['human_escalation'] is True
    assert outage['escalation_reasons'] == ['active_outage']


def test_command_full_export_matches_canonical_builder(command):
    from types import SimpleNamespace

    from apps.intake.sample_data import samples
    from apps.triage.export import build_record
    from apps.triage.schemas import validate_analysis

    records = execute_assessment(command)
    for record, case, payload in zip(records, samples(), assessment_payloads(), strict=True):
        # Normalize only generated identifiers, wall times and measured latency.
        record['request']['id'] = 'request'
        record['request']['received_at'] = 'received'
        record['provenance']['completed_at'] = 'completed'
        record['provenance']['accepted_attempt_id'] = 'attempt'
        record['processing']['attempts'][0]['id'] = 'attempt'
        record['processing']['attempts'][0]['latency_ms'] = 0
        expected = build_record(
            request={'id': 'request', 'received_at': 'received',
                     'source': case['source'], 'message': case['message']},
            analysis=validate_analysis(payload, case['message']),
            output=SimpleNamespace(model='gpt-6.1-terra', prompt_version='triage_v1',
                                   schema_version='1.0'),
            completed_at='completed', attempt_id='attempt',
            attempts=[{'id': 'attempt', 'error': None, 'latency_ms': 0,
                       'usage': {'input_tokens': 10, 'output_tokens': 20,
                                 'total_tokens': 30}}])
        assert record == expected


@pytest.mark.parametrize('artifact', ['prompt', 'schema_text'])
@pytest.mark.parametrize('partial', [False, True])
def test_artifact_change_blocks_resume(command, monkeypatch, artifact, partial):
    from apps.triage.providers.openai_provider import OpenAIProvider
    run, client, _, _, _ = command
    client.responses.create.side_effect = ([valid_response(), RuntimeError('interrupted')]
                                         if partial else [valid_response()] * 5)
    if partial:
        with pytest.raises(RuntimeError):
            run()
    else:
        run()
    count = client.responses.create.call_count
    original = OpenAIProvider.__init__
    def init(self, **kwargs):
        original(self, **kwargs)
        setattr(self, artifact, getattr(self, artifact) + '\n')
    monkeypatch.setattr(OpenAIProvider, '__init__', init)
    with pytest.raises(ValueError, match='Prompt/schema mismatch'):
        run()
    assert client.responses.create.call_count == count


def test_http_write_failure_retains_usage(command, monkeypatch):
    run, client, _, _, events = command
    client.responses.create.side_effect = openai.InternalServerError(
        'secret', response=httpx.Response(500, request=httpx.Request('POST', 'https://example.test')),
        body={'usage': {'input_tokens': 12}, 'secret': 'secret'})
    original = Runner.append
    def append(self, event):
        if event['state'] == 'raw_response':
            raise OSError('disk error')
        original(self, event)
    monkeypatch.setattr(Runner, 'append', append)
    with pytest.raises(OSError):
        run()
    records = events()
    assert records[-1]['usage'] == {'input_tokens': 12}
    assert records[0]['reservation']
    assert 'secret' not in json.dumps(records)


@pytest.mark.parametrize('changed', [None, 'prompt', 'schema'])
def test_execute_then_dry_identity(command, monkeypatch, changed):
    run, client, factory, _, _ = command
    client.responses.create.side_effect = [valid_response(i) for i in range(5)]
    run()
    if changed:
        from apps.triage.providers import openai_provider
        original = openai_provider.artifact_identity
        def modified(*args, **kwargs):
            identity = original(*args, **kwargs)
            identity[changed] = 'changed'
            return identity
        monkeypatch.setattr(openai_provider, 'artifact_identity', modified)
    result = run(False)
    assert result == {'dry_run': True, 'pending': 5 if changed else 0}
    factory.assert_called_once()
    assert client.responses.create.call_count == 5


def test_serial_usage_release_and_budget_exhaustion(command):
    run, client, _, path, events = command
    config = json.loads(path.read_text())
    # One full reservation fits; five simultaneous maxima do not.
    config['budget'] = '18'
    path.write_text(json.dumps(config))
    client.responses.create.side_effect = [valid_response(i) for i in range(5)]
    run()
    assert client.responses.create.call_count == 5
    assert len([e for e in events() if e['state'] == 'reconciled']) == 5
    run()
    assert len([e for e in events() if e['state'] == 'reconciled']) == 5


def test_missing_usage_exhausts_serial_budget(command):
    run, client, _, path, events = command
    config = json.loads(path.read_text())
    config['budget'] = '18'
    path.write_text(json.dumps(config))
    response = valid_response()
    response.usage = None
    client.responses.create.return_value = response
    with pytest.raises(ValueError, match='Budget'):
        run()
    assert client.responses.create.call_count == 1
    assert not any(e['state'] == 'reconciled' for e in events())
