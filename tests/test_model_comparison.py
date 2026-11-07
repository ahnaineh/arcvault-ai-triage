import json
import os
from io import StringIO
from pathlib import Path
from unittest.mock import Mock

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.triage.providers.openai_provider import (
    BoundedOpenAIAdapter,
    OpenAIProvider,
    safe_usage,
)
from tests.test_acceptance_command import valid_response


def test_luna_reasoning_usage_and_strict_request():
    client = Mock()
    client.with_options.return_value = client
    response = valid_response()
    response.model = 'gpt-6-luna'
    client.responses.create.return_value = response
    provider = OpenAIProvider(client=client, model='gpt-6-luna', reasoning_effort='high', max_output_tokens=25000)
    provider.analyze('How do roles work?')
    request = client.responses.create.call_args.kwargs
    assert request['model'] == 'gpt-6-luna'
    assert request['reasoning'] == {'effort': 'high'}
    assert request['max_output_tokens'] == 25000
    assert request['text']['format']['strict'] is True
    client.with_options.assert_called_with(max_retries=0, timeout=30)
    assert safe_usage({'input_tokens': 5, 'output_tokens': 105,
        'output_tokens_details': {'reasoning_tokens': 100}})['reasoning_tokens'] == 100


def test_luna_bounds_reject_cheap_unproven_reservation():
    config = json.loads(Path('config/acceptance/benchmark.json').read_text())
    config.update(model='gpt-6-luna', input_price_per_million='.1', output_price_per_million='.5')
    adapter = BoundedOpenAIAdapter(client=Mock(), config=config)
    with pytest.raises(ValueError, match='prices'):
        adapter.preflight(['example'], config)
    assert not adapter.maximum_input_bound(model='gpt-6-luna', bound=1000)


def test_paired_command_freezes_and_resumes_without_duplicate_calls(tmp_path, monkeypatch):
    monkeypatch.setattr('apps.triage.acceptance.Path.resolve', lambda self: self)
    monkeypatch.setenv('OPENAI_API_KEY', 'synthetic-offline-key')
    client = Mock()
    client.with_options.return_value = client
    def respond(**kwargs):
        response = valid_response()
        response.model = kwargs['model']
        return response
    client.responses.create.side_effect = respond
    monkeypatch.setattr('openai.OpenAI', Mock(return_value=client))
    directory = os.path.relpath(tmp_path / 'comparison')
    for _ in range(2):
        call_command('compare_models', '--run-dir', directory, '--execute', stdout=StringIO())
    assert client.responses.create.call_count == 100
    luna = json.loads((tmp_path / 'comparison/gpt-6-luna/config.json').read_text())
    terra = json.loads((tmp_path / 'comparison/gpt-6.1-terra/config.json').read_text())
    assert float(terra['reconciled_history']['known_cost']) > float(luna['reconciled_history']['known_cost'])
    manifest = tmp_path / 'comparison/freeze.json'
    data = json.loads(manifest.read_text()); data['prompt'] = 'changed'
    manifest.write_text(json.dumps(data))
    with pytest.raises(CommandError, match='identity changed'):
        call_command('compare_models', '--run-dir', directory, '--execute')
    assert client.responses.create.call_count == 100


def test_terminal_validation_failure_is_not_retried_and_retains_maximum(tmp_path, monkeypatch):
    from apps.triage.acceptance import Runner, accounted
    from apps.triage.providers.openai_provider import ProviderError
    monkeypatch.setattr('apps.triage.acceptance.Path.resolve', lambda self: self)
    config = json.loads(Path('config/acceptance/benchmark.json').read_text())
    provider = Mock(enforces_bounds=True)
    provider.inference_identity.return_value = None
    provider.side_effect = ProviderError('provider_invalid', usage={'input_tokens': 5, 'output_tokens': 10})
    runner = Runner(os.path.relpath(tmp_path / 'terminal'), config, terminal_provider_failures=True)
    cases = [{'sample_id': 'broken', 'source': 'Email', 'message': 'Broken'}]
    records = runner.run(cases, provider, execute=True)
    assert records[0]['error']
    assert runner.run(cases, provider, execute=True) == records
    assert provider.call_count == 1
    events = [json.loads(x) for x in runner.path.read_text().splitlines()]
    assert accounted(events, config)[0] == __import__('decimal').Decimal('11.617584')
