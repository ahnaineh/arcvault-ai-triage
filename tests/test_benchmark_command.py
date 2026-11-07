import json
import os
from io import StringIO
from pathlib import Path

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

ROOT = Path(__file__).resolve().parents[1]


def test_benchmark_dry_run_and_locked_test(tmp_path, monkeypatch):
    monkeypatch.setattr('apps.triage.acceptance.Path.resolve', lambda self: self)
    output = StringIO()
    call_command('run_benchmark', '--run-dir', os.path.relpath(tmp_path / 'runtime'),
                 '--config', str(ROOT / 'config/acceptance/benchmark.json'), '--phase', 'baseline', stdout=output)
    assert json.loads(output.getvalue()) == {'phase': 'baseline', 'cases': 25, 'execute': False}
    assert not (tmp_path / 'runtime/events.jsonl').exists()
    with pytest.raises(CommandError, match='Frozen identity'):
        call_command('run_benchmark', '--run-dir', os.path.relpath(tmp_path / 'runtime'),
                     '--config', str(ROOT / 'config/acceptance/benchmark.json'), '--phase', 'test')


def test_validation_cannot_skip_development(tmp_path):
    with pytest.raises(CommandError, match='preceding phase'):
        call_command('run_benchmark', '--run-dir', os.path.relpath(tmp_path / 'runtime'),
                     '--config', str(ROOT / 'config/acceptance/benchmark.json'), '--phase', 'validation', '--execute')


def test_all_phases_share_ledger_and_frozen_test_resumes(tmp_path, monkeypatch):
    from unittest.mock import Mock

    from tests.test_acceptance_command import valid_response
    monkeypatch.setattr('apps.triage.acceptance.Path.resolve', lambda self: self)
    monkeypatch.setenv('OPENAI_API_KEY', 'synthetic-offline-key')
    client = Mock()
    client.with_options.return_value = client
    client.responses.create.side_effect = lambda **kwargs: valid_response()
    monkeypatch.setattr('openai.OpenAI', Mock(return_value=client))
    directory = os.path.relpath(tmp_path / 'runtime')
    def run(phase, *extra):
        call_command('run_benchmark', '--run-dir', directory, '--config',
            str(ROOT / 'config/acceptance/benchmark.json'), '--phase', phase, '--execute', *extra, stdout=StringIO())
    for phase in ('baseline', 'development', 'validation'):
        run(phase)
    run('validation', '--freeze')
    run('test')
    count = client.responses.create.call_count
    run('test')
    assert client.responses.create.call_count == count == 70
    run('assessment')
    journal = [json.loads(line) for line in (tmp_path / 'runtime/events.jsonl').read_text().splitlines()]
    assert sum(e['state'] == 'reconciled' for e in journal) == 75
    assert all(e.get('request_id') for e in journal if e['state'] == 'raw_response')
