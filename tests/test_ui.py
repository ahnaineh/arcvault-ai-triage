from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.test import Client, override_settings

from apps.triage.models import Request
from apps.triage.tasks import process
from tests.test_backend import analysis

pytestmark = pytest.mark.django_db


@override_settings(STORAGES={'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'}})
def test_session_webhook_and_pages(django_user_model):
    client = Client(enforce_csrf_checks=True)
    assert client.get('/').status_code == 302
    assert client.get('/tester/').status_code == 302
    user = django_user_model.objects.create_user('reviewer', password='test-password')
    client.force_login(user)
    assert client.get('/logout/').status_code == 405
    assert client.get('/tester/').status_code == 200
    token = client.cookies['csrftoken'].value
    data = {'source': 'Email', 'message': 'usage?', 'idempotency_key': 'ui-test'}
    assert client.post('/api/v1/requests/', data, content_type='application/json').status_code == 403
    with patch('apps.intake.service.dispatch'):
        response = client.post('/api/v1/requests/', data, content_type='application/json', HTTP_X_CSRFTOKEN=token)
    assert response.status_code == 202
    row = Request.objects.get()
    detail = f'/requests/{row.pk}/'
    assert b'No accepted analysis yet' in client.get(detail).content
    assert client.get(response['Location'] + 'export/').status_code == 409
    output = SimpleNamespace(analysis=analysis(), model='mock', prompt_version='v1', schema_version='v1', latency_ms=1, usage=None)
    with patch('apps.triage.tasks.get_provider') as provider:
        provider.return_value.analyze.return_value = output
        process(str(row.pk))
    assert b'Technical Support' in client.get(detail).content
    assert client.get(response['Location'] + 'export/').status_code == 200
    row.refresh_from_db()
    result = row.accepted_result
    result.record['summary'] = '<script>alert(1)</script>'
    result.record['decision']['human_escalation'] = True
    result.save()
    row.message = '<img src=x onerror=alert(1)>'
    row.save()
    content = client.get(detail).content
    assert b'&lt;script&gt;' in content and b'<script>alert' not in content
    assert b'&lt;img' in content
    assert str(row.pk).encode() in client.get('/?queue=review').content
    assert client.post('/logout/', HTTP_X_CSRFTOKEN=token).status_code == 302
    assert client.get(detail).status_code == 302
    assert client.get(response['Location'] + 'export/').status_code == 401


@pytest.mark.django_db(transaction=True)
@override_settings(INTAKE_BEARER_TOKEN='synthetic-token')
def test_accepted_response_lost_retry_keeps_single_request():
    client = Client()
    payload = {'source': 'Email', 'message': 'usage?', 'idempotency_key': 'lost-response'}
    auth = {'HTTP_AUTHORIZATION': 'Bearer synthetic-token'}
    with patch('apps.intake.service.dispatch') as dispatch:
        accepted = client.post('/api/v1/requests/', payload, content_type='application/json', **auth)
        assert accepted.status_code == 202
        # Simulate transport loss after acceptance: discard the response and retry.
        retry = client.post('/api/v1/requests/', payload, content_type='application/json', **auth)
        assert retry.status_code == 200
        assert retry.json()['id'] == accepted.json()['id']
        assert Request.objects.count() == 1
        assert Request.objects.get().idempotency_key == payload['idempotency_key']
        assert dispatch.call_count == 1
