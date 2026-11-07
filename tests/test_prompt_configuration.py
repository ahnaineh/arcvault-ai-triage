"""Exercise SDK request instructions, rather than trusting metadata labels."""
import hashlib
import json

import pytest

from apps.triage.providers.openai_provider import ArtifactIdentity, artifact_identity
from apps.triage.tasks import get_provider
from tests.test_acceptance_command import valid_response

pytest_plugins = ['tests.test_acceptance_command']


@pytest.mark.parametrize('version', ['triage_v3', 'triage_v1'])
def test_application_acceptance_identity_and_resume_use_same_selection(command, settings, version):
    run, client, factory, path, events = command
    settings.OPENAI_PROMPT_VERSION = version
    if version == 'triage_v1':
        config = json.loads(path.read_text())
        config['prompt_version'] = version  # Legacy is always an explicit selection.
        path.write_text(json.dumps(config))
    client.responses.create.side_effect = lambda **kwargs: valid_response()
    app = get_provider()
    app.analyze('How do access roles work?')
    app_request = client.responses.create.call_args.kwargs
    selected_hash = hashlib.sha256(app_request['instructions'].encode()).hexdigest()
    assert app.prompt_version == version
    assert ArtifactIdentity(prompt_version=version).inference_identity()['prompt'] == selected_hash
    assert artifact_identity(prompt_version=version)['prompt'] == selected_hash
    run()
    assert all(hashlib.sha256(c.kwargs['instructions'].encode()).hexdigest() == selected_hash
               for c in client.responses.create.call_args_list)
    assert all(e['inference']['prompt'] == selected_hash for e in events() if e['state'] == 'reserved')
    count = client.responses.create.call_count
    factory_count = factory.call_count
    assert run(False) == {'dry_run': True, 'pending': 0}
    assert factory.call_count == factory_count
    run()
    assert client.responses.create.call_count == count
    config = json.loads(path.read_text())
    config['prompt_version'] = 'triage_v1' if version == 'triage_v3' else 'triage_v3'
    path.write_text(json.dumps(config))
    for execute in (False, True):
        with pytest.raises(ValueError, match='mismatch'):
            run(execute)
    assert client.responses.create.call_count == count


def test_benchmark_default_request_matches_offline_identity(tmp_path, monkeypatch, settings):
    import os
    from io import StringIO
    from unittest.mock import Mock

    from django.core.management import call_command

    settings.OPENAI_PROMPT_VERSION = 'triage_v3'
    monkeypatch.setattr('apps.triage.acceptance.Path.resolve', lambda self: self)
    monkeypatch.setenv('OPENAI_API_KEY', 'synthetic-offline-key')
    client = Mock()
    client.with_options.return_value = client
    client.responses.create.side_effect = lambda **kwargs: valid_response()
    monkeypatch.setattr('openai.OpenAI', Mock(return_value=client))
    directory = os.path.relpath(tmp_path / 'benchmark')
    args = ['--run-dir', directory, '--config', 'config/acceptance/benchmark.json', '--phase', 'baseline']
    call_command('run_benchmark', *args, '--execute', stdout=StringIO())
    expected = ArtifactIdentity().inference_identity()['prompt']
    assert all(hashlib.sha256(c.kwargs['instructions'].encode()).hexdigest() == expected
               for c in client.responses.create.call_args_list)
    manifest = json.loads((tmp_path / 'benchmark/baseline.manifest.json').read_text())
    from apps.triage.acceptance import digest
    from apps.triage.providers.openai_provider import prompt_text
    assert manifest['prompt'] == digest(prompt_text())
    call_command('run_benchmark', *args, stdout=StringIO())
    call_command('run_benchmark', *args, '--execute', stdout=StringIO())
    assert client.responses.create.call_count == 25
