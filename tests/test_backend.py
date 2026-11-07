from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.test import Client, override_settings
from django.utils import timezone

from apps.triage.models import Request, Result
from apps.triage.schemas import validate_analysis
from apps.triage.tasks import process

pytestmark = pytest.mark.django_db


def analysis():
    return validate_analysis({'category': 'Technical Question', 'priority': 'Low', 'confidence': .9,
        'core_issue': 'Usage question.', 'entities': [], 'urgency': {'level': 'Unknown', 'evidence': []},
        'signals': {k: {'value': False, 'evidence': []} for k in ['active_service_outage', 'insufficient_information', 'conflicting_intents']},
        'billing_comparison': None, 'summary_sentences': ['Customer asks about usage.', 'No further details supplied.']}, 'usage?')


@override_settings(INTAKE_BEARER_TOKEN='test-token')
def test_api(django_user_model):
    c = Client(enforce_csrf_checks=True)
    url = '/api/v1/requests/'
    data = {'source': 'Email', 'message': ' usage? ', 'idempotency_key': 'one'}
    assert c.post(url, data, content_type='application/json').status_code == 401
    user = django_user_model.objects.create_user('reviewer')
    c.force_login(user)
    assert c.post(url, data, content_type='application/json').status_code == 403
    assert c.post(url, data, content_type='application/json', HTTP_AUTHORIZATION='Bearer wrong').status_code == 401
    auth = {'HTTP_AUTHORIZATION': 'Bearer test-token'}
    response = c.post(url, data, content_type='application/json', **auth)
    assert response.status_code == 202
    assert c.post(url, data, content_type='application/json', **auth).status_code == 200
    assert c.post(url, data | {'message': 'different'}, content_type='application/json', **auth).status_code == 409
    assert c.post(url, data | {'extra': 1}, content_type='application/json', **auth).status_code == 400
    assert c.get(response['Location']).json()['attempt_count'] == 0
    assert c.get(response['Location'] + 'export/').status_code == 409
    assert Request.objects.get().message == ' usage? '


def test_pipeline():
    row = Request.objects.create(principal='service', source='Email', message='usage?')
    output = SimpleNamespace(analysis=analysis(), model='mock', prompt_version='v1', schema_version='v1', latency_ms=12, usage=None)
    with patch('apps.triage.tasks.get_provider') as provider:
        provider.return_value.analyze.return_value = output
        process(str(row.pk))
        process(str(row.pk))
        assert provider.return_value.analyze.call_count == 1
    row.refresh_from_db()
    assert row.status == 'completed'
    saved = Result.objects.get().record
    c = Client()
    with override_settings(INTAKE_BEARER_TOKEN='token'):
        assert c.get(f'/api/v1/requests/{row.pk}/export/', HTTP_AUTHORIZATION='Bearer token').json() == saved
    assert saved['analysis'] == output.analysis.model_dump(mode='json')
    assert saved['decision']['final_destination'] == 'Technical Support'


def test_retry_exhaustion():
    row = Request.objects.create(principal='service', source='Email', message='usage?')
    exc = RuntimeError('PRIVATE')
    exc.code = 'provider_transient'
    with patch('apps.triage.tasks.get_provider', side_effect=exc):
        for _ in range(3):
            Request.objects.filter(pk=row.pk).update(next_attempt_at=timezone.now())
            process(str(row.pk))
    row.refresh_from_db()
    assert row.status == 'failed'
    assert row.attempts.count() == 3
    assert row.error == 'provider_transient'
    assert not Result.objects.exists()


def test_dispatch_failure():
    from apps.intake.service import dispatch
    row = Request.objects.create(principal='service', source='Email', message='usage?')
    with patch('apps.triage.tasks.process.apply_async', side_effect=RuntimeError('PRIVATE')):
        dispatch(row.pk)
    row.refresh_from_db()
    assert row.status == 'pending'
    assert row.dispatch_error == 'dispatch_failed'
