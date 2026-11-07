import hashlib
import json
from io import StringIO
from pathlib import Path
from unittest.mock import Mock

import httpx2 as httpx
import openai
import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.triage.acceptance import Runner
from apps.triage.providers.openai_provider import ProviderError
from tests.test_openai_provider import envelope

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def command(tmp_path, monkeypatch):
    monkeypatch.setattr('apps.triage.acceptance.Path.resolve', lambda self: self)
    monkeypatch.chdir(tmp_path)
    config = json.loads((ROOT / 'config/acceptance/terra.json').read_text())
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


@pytest.mark.parametrize('http_failure', [False, True], ids=['success-response', 'http-error'])
def test_response_write_failure_retains_usage(command, monkeypatch, http_failure):
    run, client, _, _, events = command
    if http_failure:
        client.responses.create.side_effect = openai.InternalServerError(
            'secret', response=httpx.Response(500, request=httpx.Request('POST', 'https://example.test')),
            body={'usage': {'input_tokens': 12}, 'secret': 'secret'})
    else:
        client.responses.create.return_value = valid_response()
    original = Runner.append
    def append(self, event):
        if event['state'] == 'raw_response':
            raise OSError('disk error')
        original(self, event)
    monkeypatch.setattr(Runner, 'append', append)
    with pytest.raises(OSError):
        run()
    records = events()
    assert [event['state'] for event in records] == ['reserved', 'failed']
    expected_usage = ({'input_tokens': 12} if http_failure else
                      {'input_tokens': 10, 'output_tokens': 20, 'total_tokens': 30})
    assert records[-1]['usage'] == expected_usage
    assert records[0]['reservation']
    assert 'secret' not in json.dumps(records)


def test_export_error_no_partial_rewrite(command, monkeypatch):
    run, client, _, _, events = command
    client.responses.create.side_effect = [valid_response(i) for i in range(5)]
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


def test_command_assessment_export_and_resume(command):
    from apps.intake.sample_data import samples
    run, client, _, _, events = command
    payloads = assessment_payloads()
    responses = []
    for payload in payloads:
        response = valid_response()
        response.output[0].content[0].text = json.dumps(payload)
        responses.append(response)
    client.responses.create.side_effect = responses
    run()
    records = json.loads(Path('runtime/assessment_outputs.json').read_text())
    assert len(records) == 5
    for record, case, payload in zip(records, samples(), payloads, strict=True):
        assert set(record) == {'schema_version', 'request', 'analysis', 'decision',
                               'summary', 'provenance', 'processing', 'review'}
        assert record['schema_version'] == '1.0'
        assert record['review'] is None
        assert set(record['request']) == {'id', 'source', 'message', 'received_at'}
        assert record['request']['source'] == case['source']
        assert record['request']['message'] == case['message']
        assert record['request']['id'] and record['request']['received_at']
        assert record['analysis'] == payload
        assert record['summary'] == 'One. Two.'
        provenance = record['provenance']
        assert provenance['completed_at']
        assert provenance['accepted_attempt_id'] == record['request']['id']
        assert provenance == {
            'model': 'gpt-6.1-terra', 'prompt_version': 'triage_v4',
            'schema_version': '1.0', 'policy_version': '1.1',
            'prompt_sha256': hashlib.sha256((ROOT / 'prompts/triage_v4.txt').read_bytes()).hexdigest(),
            'schema_sha256': hashlib.sha256((ROOT / 'contracts/analysis.schema.json').read_bytes()).hexdigest(),
            'completed_at': provenance['completed_at'],
            'accepted_attempt_id': record['request']['id']}
        attempt, = record['processing']['attempts']
        assert attempt['latency_ms'] >= 0
        assert record['processing'] == {
            'attempts': [{'id': record['request']['id'], 'error': None,
                          'latency_ms': attempt['latency_ms'],
                          'usage': {'input_tokens': 10, 'output_tokens': 20, 'total_tokens': 30}}],
            'estimated_cost': None, 'unknown_cost': True}
    assert len([event for event in events() if event['state'] == 'completed']) == 5
    run()
    assert client.responses.create.call_count == 5
    client.with_options.assert_called_with(max_retries=0, timeout=60)
    assert [(record['decision']['standard_destination'], record['decision']['final_destination'],
             record['decision']['human_escalation'], record['decision']['escalation_reasons'])
            for record in records] == [
        ('Engineering', 'Engineering', False, []),
        ('Product', 'Product', False, []),
        ('Billing', 'Billing', False, []),
        ('Technical Support', 'Technical Support', False, []),
        ('Engineering', 'Human Review', True, ['active_outage'])]
    for index, record in enumerate(records):
        assert set(record['decision']) == {'standard_destination', 'final_destination',
            'human_escalation', 'escalation_reasons', 'reported_overcharge', 'comparison_assumptions'}
        if index != 2:
            assert record['decision']['reported_overcharge'] is None
            assert record['decision']['comparison_assumptions'] == []
    billing = records[2]['decision']
    assert billing['reported_overcharge'] == '260'
    assert billing['comparison_assumptions'] == [
        'Unqualified $ interpreted as USD in synthetic domain',
        'Unqualified $ interpreted as USD in synthetic domain',
        'Direct invoice/monthly contract comparison treated as one monthly charge']


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
    if changed:
        with pytest.raises(ValueError, match='Prompt/schema'):
            run(False)
    else:
        assert run(False) == {'dry_run': True, 'pending': 0}
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
