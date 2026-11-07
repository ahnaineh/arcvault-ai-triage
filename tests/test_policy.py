import json
from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import ValidationError

from apps.triage.policy import decide, decide_projection, normalize_billing
from apps.triage.schemas import Comparison, validate_analysis

CASES = json.loads(Path('tests/fixtures/policy_cases.json').read_text())['cases']
@pytest.mark.parametrize('case', CASES, ids=lambda c:c['id'])
def test_controlled(case):
    assert decide_projection(**case['input']) == case['expected']

def payload():
    return {'category': 'Billing Issue', 'priority': 'Low', 'confidence': .9, 'core_issue': 'Invoice dispute.', 'entities': [], 'urgency': {'level':'Unknown','evidence':[]}, 'signals': {k:{'value':False,'evidence':[]} for k in ['active_service_outage','insufficient_information','conflicting_intents']}, 'billing_comparison': None, 'summary_sentences': ['Customer reports an invoice dispute.', 'Review requested.']}

def money(amount, currency='$', period='monthly', components='subscription'):
    return {'amount': amount,'currency': currency,'period': period,'components': components,'evidence': ['invoice ' + (amount or '')]}

@pytest.mark.parametrize('field,value', [('confidence',float('nan')),('confidence',float('inf')),('confidence',True),('confidence','0.9'),('priority','Urgent'),('core_issue',' '),('summary_sentences',['Only one.']),('extra','queue')])
def test_invalid_shape(field,value):
    data=payload(); data[field]=value
    with pytest.raises(ValidationError): validate_analysis(data,'invoice')

@pytest.mark.parametrize('amount',['NaN','Infinity','-1','1,000','1e3','$20',' 20'])
def test_money_rejected(amount):
    with pytest.raises(ValidationError): Comparison.model_validate({'billed':money(amount),'expected':money('10')})

def test_context_and_exact_evidence():
    data=payload(); data['signals']['active_service_outage']={'value':None,'evidence':[]}
    with pytest.raises(ValidationError): validate_analysis(data,'invoice')
    data['signals']['active_service_outage']['evidence']=['Invoice']
    with pytest.raises(ValidationError): validate_analysis(data,'invoice')
    data['signals']['active_service_outage']['evidence']=['invoice']
    assert decide(validate_analysis(data,'invoice'))['escalation_reasons']==['outage_scope_unresolved']

@pytest.mark.parametrize('billed,expected,status,difference', [
    (money('760'),money('500'),'comparable_usd','260'),
    (money('1.01'),money('601.02'),'comparable_usd','-600.01'),
    (money('1000','EUR'),money('1','EUR'),'unresolved',None),
    (money('1000',None),money('1'),'unresolved',None),
    (money('1000',period='annual'),money('1'),'unresolved',None),
    (money('1000',components=None),money('1'),'unresolved',None),
    (money(None),money('1'),'unresolved',None),
    (money('1000',period='invoice'),money('1'),'comparable_usd','999'),
])
def test_billing_and_composition(billed,expected,status,difference):
    data=payload(); data['billing_comparison']={'billed':billed,'expected':expected}
    analysis=validate_analysis(data,'invoice ' + (billed['amount'] or '') + ' invoice ' + (expected['amount'] or ''))
    actual, delta, assumptions=normalize_billing(analysis.billing_comparison)
    assert actual==status
    assert delta==(Decimal(difference) if difference else None)
    decision=decide(analysis)
    assert decision['reported_overcharge']==difference
    assert decision['human_escalation']==(status=='unresolved' or Decimal(difference)>500)
    assert bool(assumptions) == (billed["currency"] == "$" or expected["currency"] == "$")

@pytest.mark.parametrize('basis', ['Unknown', 'bogus', 'annual'])
def test_unknown_or_incompatible_basis(basis):
    data=payload()
    data['billing_comparison']={'billed':money('760',period=basis), 'expected':money('500',period=basis if basis != 'annual' else 'monthly')}
    assert decide(validate_analysis(data,'invoice 760 invoice 500'))['human_escalation']

@pytest.mark.parametrize('evidence', [[], ['hello'], ['7600']])
def test_unsupported_amount(evidence):
    data=payload()
    data['billing_comparison']={'billed':money('760'), 'expected':money('500')}
    data['billing_comparison']['billed']['evidence']=evidence
    with pytest.raises(ValidationError): validate_analysis(data,'hello 7600 invoice 500')

def test_boundary_nan():
    analysis=validate_analysis(payload(),'hello')
    analysis.confidence=float('nan')
    with pytest.raises(ValueError): decide(analysis)
    analysis=validate_analysis(payload(),'hello').model_copy(update={'confidence':float('nan')})
    with pytest.raises(ValueError): decide(analysis)

def test_export_and_nested_mutation():
    analysis=validate_analysis(payload(),'hello')
    exported=analysis.model_dump()
    exported['confidence']=0
    assert not decide(analysis)['human_escalation']
    analysis.signals.insufficient_information.value=True
    with pytest.raises(ValueError): decide(analysis)

def test_comma_currency_numeric_support():
    data=payload()
    data['billing_comparison']={'billed':money('1760'), 'expected':money('500')}
    data['billing_comparison']['billed']['evidence']=['US$1,760']
    assert decide(validate_analysis(data,'US$1,760 invoice 500'))['reported_overcharge']=='1260'


def test_unequal_decimal_scales():
    data = payload()
    data['billing_comparison'] = {'billed': money('100000000000000000000'), 'expected': money('0.000000000000000000001')}
    analysis = validate_analysis(data, 'invoice 100000000000000000000 invoice 0.000000000000000000001')
    assert decide(analysis)['reported_overcharge'] == '99999999999999999999.999999999999999999999'


@pytest.mark.parametrize('amount,excerpt,valid', [('760', '$760.', True), ('500.00', '$500.00.', True), ('760', '$7600.', False), ('760', '$760.01', False), ('760', '.760', False), ('760', '$1760', False)])
def test_money_sentence_punctuation(amount, excerpt, valid):
    data = payload()
    fact = money(amount)
    fact['evidence'] = [excerpt]
    data['billing_comparison'] = {'billed': fact, 'expected': fact}
    if valid:
        validate_analysis(data, excerpt)
    else:
        with pytest.raises(ValidationError):
            validate_analysis(data, excerpt)
