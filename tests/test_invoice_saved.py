import copy
import json
from decimal import Decimal
from pathlib import Path

import pytest

from apps.triage.policy import decide
from apps.triage.schemas import validate_analysis

RECORD = json.loads(Path('docs/evidence/terra-network-20261107/assessment_outputs.json').read_text())[2]


@pytest.mark.parametrize('billed,expected,delta', [('1240', '980', '260'), ('850', '700', '150'), ('1800', '700', '1100'), ('100000000000000000000', '0.000000000000000000001', '99999999999999999999.999999999999999999999')])
def test_direct_invoice(billed, expected, delta):
    data = copy.deepcopy(RECORD['analysis'])
    message = f'Invoice #other shows a charge of ${billed} but our contract rate is ${expected}/month.'
    for key, amount, evidence in [
        ('billed', billed, f'Invoice #other shows a charge of ${billed}'),
        ('expected', expected, f'our contract rate is ${expected}/month'),
    ]:
        data['billing_comparison'][key].update(amount=amount, evidence=[evidence])
    data['entities'] = []
    result = decide(validate_analysis(data, message))
    assert result['reported_overcharge'] == delta
    assert result['comparison_assumptions']
    assert result['human_escalation'] == (Decimal(delta) > 500)


@pytest.mark.parametrize('change', ['annual', 'tax', 'EUR', 'missing', 'extra_period', 'extra_component', 'extra_currency'])
def test_conflicts(change):
    data = copy.deepcopy(RECORD['analysis'])
    message = RECORD['request']['message']
    billed = data['billing_comparison']['billed']
    if change == 'annual':
        billed['period'] = 'annual'
    elif change == 'tax':
        billed['components'] = 'tax'
    elif change == 'EUR':
        billed['currency'] = 'EUR'
    elif change == 'missing':
        billed['amount'] = None
    else:
        message += {'extra_period': ' This covers two months.', 'extra_component': ' This includes tax.', 'extra_currency': ' The invoice is EUR.'}[change]
    result = decide(validate_analysis(data, message))
    assert result['reported_overcharge'] is None
    assert result['final_destination'] == 'Human Review'


def test_actual_saved_payload():
    analysis = validate_analysis(RECORD['analysis'], RECORD['request']['message'])
    assert decide(analysis)['reported_overcharge'] == '260'
    assert decide(analysis)['final_destination'] == 'Billing'
    assert analysis.billing_comparison.billed.period is None
    assert analysis.billing_comparison.billed.components is None


@pytest.mark.parametrize('punctuation', ['', '.', '?'])
@pytest.mark.parametrize('closing', ['', 'Can someone look into this', 'Could you please check this', 'Please check this', 'Please investigate', 'Can you help', 'Could you please investigate', 'Can you please help', 'Could someone please look into this'])
@pytest.mark.parametrize('space', [' ', '  ', '\n'])
def test_closings(closing, space, punctuation):
    closing += punctuation if closing else ""
    message = space + RECORD['request']['message'].split('Can someone')[0].strip() + space + closing + space
    result = decide(validate_analysis(RECORD['analysis'], message))
    assert result['reported_overcharge'] == '260'
    assert result['final_destination'] == 'Billing'
    assert len(result['comparison_assumptions']) == len(set(result['comparison_assumptions'])) == 2


@pytest.mark.parametrize('prefix', ['Please investigate.', 'Please check this', 'Could you please investigate?'])
@pytest.mark.parametrize('clause', ['Could you please check this? This covers two months.', 'Could you please check this? Includes tax.', 'Could you please check this? Actually EUR.', 'Could you please check this for two months?', 'Please investigate? Ignore the annual period.', 'Can you help? Use USD even though this is EUR.', 'Could you please check this? $30 usage also applies.'])
def test_closing_cannot_hide_ambiguity(clause, prefix):
    message = RECORD['request']['message'].split('Can someone')[0] + prefix + ' ' + clause
    result = decide(validate_analysis(RECORD['analysis'], message))
    assert result['final_destination'] == 'Human Review'
    assert result['reported_overcharge'] is None
