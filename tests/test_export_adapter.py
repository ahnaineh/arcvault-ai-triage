import copy

from evals.export_adapter import adapt
from evals.score import load, score


def test_full_application_export():
    cases = copy.deepcopy(load()[5:8])
    analysis = {
        'category': 'Incident/Outage', 'priority': 'High', 'confidence': .95,
        'core_issue': 'Dashboard unavailable to all employees.', 'entities': [],
        'urgency': {'level': 'High', 'evidence': []},
        'signals': {k: {'value': v, 'evidence': []} for k, v in
                    {'active_service_outage': True, 'insufficient_information': False,
                     'conflicting_intents': False}.items()},
        'billing_comparison': None,
        'summary_sentences': ['Employees cannot open the dashboard.', 'Service is down.'],
    }
    record = {
        'schema_version': '1.0', 'request': {'id': 'application-uuid',
            'source': 'Email', 'message': cases[0]['message'],
            'received_at': '2026-11-07T12:00:00Z'},
        'analysis': analysis,
        'decision': {'standard_destination': 'Engineering',
            'final_destination': 'Human Review', 'human_escalation': True,
            'escalation_reasons': ['active_outage'], 'reported_overcharge': None,
            'comparison_assumptions': []},
        'summary': 'Employees cannot open the dashboard. Service is down.',
        'provenance': {'model': 'offline-fixture', 'prompt_version': '1.0',
            'schema_version': '1.0', 'policy_version': '1.0',
            'completed_at': '2026-11-07T12:00:01Z', 'accepted_attempt_id': 'attempt-1'},
        'processing': {'attempts': [{'id': 'attempt-1', 'error': None,
            'latency_ms': 100, 'usage': None}], 'estimated_cost': None, 'unknown_cost': True},
        'review': {'status': 'approved'},
    }
    missing = copy.deepcopy(record)
    missing['request']['message'] = cases[1]['message']
    missing['analysis'] = None
    wrong = copy.deepcopy(record)
    wrong['request']['message'] = cases[2]['message']
    wrong['decision'].update(final_destination='Product', human_escalation=False)
    predictions = adapt([record, missing, wrong], cases)
    result = score(cases, predictions)
    assert predictions[0]['provenance'] == record['provenance']
    assert result['rows'][0]['routing']
    assert result['metrics']['operational_failures'] == {'count': 1, 'denominator': 3}
    assert result['metrics']['completed']['count'] == 2
    assert result['conditional_routing']['incorrect_automatic_routing'] == {'count': 1, 'denominator': 1}
    assert result['metrics']['summary_constraints']['count'] == 0
    assert result['rows'][0]['manual_summary_review'] == 'review_needed'


def test_low_confidence_requires_review():
    from tests.test_eval import EvaluationTests
    prediction = EvaluationTests().prediction()
    prediction['analysis']['confidence'] = .69
    assert not score(load()[:1], [prediction])['rows'][0]['routing']
    prediction['decision'].update(final_destination='Human Review', human_escalation=True,
                                  escalation_reasons=['low_confidence'])
    result = score(load()[:1], [prediction])
    assert result['rows'][0]['routing']
    assert result['metrics']['unnecessary_escalations']['count'] == 0


def test_processing_measurements():
    case = load()[0]
    record = {'request': case, 'processing': {'attempts': [
        {'latency_ms': 40}, {'latency_ms': 100}],
        'estimated_cost': 0.012, 'unknown_cost': False}}
    prediction = adapt([record], [case])[0]
    report = score([case], [prediction])
    assert report['latency_inputs_ms'] == [140]
    assert report['cost_inputs'] == [0.012]
    record['processing']['attempts'][0]['latency_ms'] = None
    record['processing']['unknown_cost'] = True
    prediction = adapt([record], [case])[0]
    assert prediction['latency_ms'] is None
    assert prediction['cost_usd'] is None
    record['processing']['attempts'] = []
    assert adapt([record], [case])[0]['latency_ms'] is None


def test_duplicate_payment_reason_matches_policy():
    from apps.triage.policy import decide_projection
    case = next(c for c in load() if c['id'] == 'development-17')
    decision = decide_projection(category='Billing Issue', confidence=.95,
        active_service_outage=False, insufficient_information=False,
        conflicting_intents=True, billing_status='unresolved', reported_overcharge=None)
    assert decision['escalation_reasons'] == case['expected_policy']['escalation_reasons']
