"""Usage reconciliation must never silently release uncertain reservations."""
import json
from decimal import Decimal
from pathlib import Path

import pytest

from apps.triage.acceptance import accounted

CONFIG = json.loads(Path('config/acceptance/benchmark.json').read_text())


def events(usage, completed=True):
    result = [{'state': 'reserved', 'request_id': 'r', 'reservation': '11.617584'},
              {'state': 'provider_returned', 'request_id': 'r', 'model': CONFIG['model'], 'usage': usage}]
    if completed:
        result.append({'state': 'completed', 'request_id': 'r'})
    return result


@pytest.mark.parametrize('usage', [None, {}, {'input_tokens': 10},
    {'input_tokens': True, 'output_tokens': 1}, {'input_tokens': -1, 'output_tokens': 1}])
def test_missing_or_invalid_usage_retains_full_reservation(usage):
    assert accounted(events(usage), CONFIG) == (Decimal('11.617584'), [])


def test_uncertain_completion_retains_reservation():
    assert accounted(events({'input_tokens': 10, 'output_tokens': 20}, False), CONFIG)[0] == Decimal('11.617584')


def test_repeated_reconciliation_is_idempotent():
    journal = events({'input_tokens': 10, 'output_tokens': 20})
    amount, settlements = accounted(journal, CONFIG)
    assert amount == Decimal('.00044')
    assert accounted(journal + settlements + settlements, CONFIG) == (amount, settlements)


def test_original_five_reconcile_without_rewriting_evidence():
    journal = [json.loads(line) for line in Path('docs/evidence/terra-network-20261107/events.jsonl').read_text().splitlines()]
    amount, settlements = accounted(journal, CONFIG)
    assert amount == Decimal('.069047')
    assert len(settlements) == 5
    assert all(s['actual_billed_cost'] is None for s in settlements)
