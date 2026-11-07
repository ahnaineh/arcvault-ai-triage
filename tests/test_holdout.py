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
