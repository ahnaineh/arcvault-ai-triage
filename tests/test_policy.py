import json
from pathlib import Path
from decimal import Decimal
import pytest
from pydantic import ValidationError
from apps.triage.schemas import validate_analysis, Comparison
from apps.triage.policy import decide_projection, normalize_billing, decide

CASES = json.loads(Path('tests/fixtures/policy_cases.json').read_text())['cases']
@pytest.mark.parametrize('case', CASES, ids=lambda c:c['id'])
def test_controlled(case):
    assert decide_projection(**case['input']) == case['expected']

def payload():
    return dict(category='Billing Issue', priority='Low', confidence=.9, core_issue='Invoice dispute.', entities=[], urgency={'level':'Unknown','evidence':[]}, signals={k:{'value':False,'evidence':[]} for k in ['active_service_outage','insufficient_information','conflicting_intents']}, billing_comparison=None, summary_sentences=['Customer reports an invoice dispute.', 'Review requested.'])

def money(amount, currency='$', period='monthly', components='subscription'):
    return dict(amount=amount,currency=currency,period=period,components=components,evidence=['invoice'])

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
    analysis=validate_analysis(data,'invoice')
    actual, delta, assumptions=normalize_billing(analysis.billing_comparison)
    assert actual==status
    assert delta==(Decimal(difference) if difference else None)
    decision=decide(analysis)
    assert decision['reported_overcharge']==difference
    assert decision['human_escalation']==(status=='unresolved' or Decimal(difference)>500)
    assert bool(assumptions) == (billed["currency"] == "$" or expected["currency"] == "$")
