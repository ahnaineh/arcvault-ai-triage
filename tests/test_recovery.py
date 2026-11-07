from datetime import timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone

from apps.triage.management.commands.recover_requests import recover
from apps.triage.models import Attempt, Request
from apps.triage.tasks import process

pytestmark = pytest.mark.django_db


def request(**kw):
    return Request.objects.create(principal='recovery', source='email', message='usage?', **kw)


@pytest.mark.parametrize('status', ['pending', 'retrying'])
def test_gap_and_broker_failure(status):
    row = request(status=status)
    with patch('apps.triage.tasks.process.apply_async', side_effect=ConnectionError):
        recover()
    row.refresh_from_db()
    assert row.dispatch_error == 'dispatch_failed'
    Request.objects.filter(pk=row.pk).update(next_attempt_at=timezone.now()-timedelta(seconds=1))
    with patch('apps.triage.tasks.process.apply_async') as publish:
        recover()
        assert publish.call_count == 1
    row.refresh_from_db()
    assert row.dispatch_error is None


@pytest.mark.parametrize('lease', [None, -1, 60])
def test_processing_recovery(lease):
    row = request(status='processing', lease_until=None if lease is None else timezone.now()+timedelta(seconds=lease))
    attempt = Attempt.objects.create(request=row)
    with patch('apps.triage.management.commands.recover_requests.dispatch') as publish:
        recover()
    row.refresh_from_db()
    attempt.refresh_from_db()
    assert publish.call_count == (0 if lease == 60 else 1)
    assert (attempt.error == 'worker_interrupted') == (lease != 60)
    assert attempt.usage is None


@pytest.mark.parametrize('status', ['completed', 'failed'])
def test_terminal(status):
    row = request(status=status)
    with patch('apps.triage.tasks.get_provider') as provider, patch('apps.triage.management.commands.recover_requests.dispatch') as publish:
        recover()
        process(str(row.pk))
    provider.assert_not_called()
    publish.assert_not_called()


def test_budget():
    row = request()
    for _ in range(3):
        Attempt.objects.create(request=row)
    with patch('apps.triage.tasks.get_provider') as provider:
        process(str(row.pk))
    provider.assert_not_called()
    row.refresh_from_db()
    assert row.status == 'failed'


@pytest.mark.parametrize('stale_error', [True, False])
def test_duplicate_and_stale_owner(stale_error):
    row = request()

    def analyze(message):
        process(str(row.pk))  # duplicate while the first owner is active
        assert row.attempts.count() == 1
        Request.objects.filter(pk=row.pk).update(lease_until=timezone.now()-timedelta(seconds=1))
        with patch('apps.triage.management.commands.recover_requests.dispatch'):
            recover()
        if stale_error:
            raise RuntimeError('old error')
        from types import SimpleNamespace

        from tests.test_backend import analysis
        return SimpleNamespace(analysis=analysis(), model='mock', prompt_version='v1', schema_version='v1', latency_ms=12, usage=None)

    with patch('apps.triage.tasks.get_provider') as provider:
        provider.return_value.analyze.side_effect = analyze
        process(str(row.pk))
    row.refresh_from_db()
    assert row.status == 'retrying'
    assert row.error is None
    assert not hasattr(row, 'accepted_result')


@pytest.mark.django_db(transaction=True)
def test_postgres_concurrent_claim():
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier, Event

    from django.db import close_old_connections, connection, connections

    if connection.vendor != 'postgresql':
        pytest.skip('requires PostgreSQL row locks')
    row = request()
    started = Event()
    release = Event()
    gate = Barrier(2)

    def analyze(message):
        started.set()
        assert release.wait(10)
        raise RuntimeError('offline')

    def run():
        close_old_connections()
        try:
            gate.wait(timeout=10)
            process(str(row.pk))
        finally:
            connections.close_all()

    with patch('apps.triage.tasks.get_provider') as provider:
        provider.return_value.analyze.side_effect = analyze
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(run) for _ in range(2)]
            assert started.wait(10)
            release.set()
            for future in futures:
                future.result(timeout=10)
        assert provider.return_value.analyze.call_count == 1
    assert row.attempts.count() == 1


def test_commit_without_publication(django_capture_on_commit_callbacks):
    from apps.intake.service import accept

    with django_capture_on_commit_callbacks(execute=False) as callbacks:
        row, created = accept('gap', {'source': 'Email', 'message': 'usage?'})
    assert created and len(callbacks) == 1
    with patch('apps.triage.management.commands.recover_requests.dispatch') as publish:
        recover()
    publish.assert_called_once_with(row.pk, countdown=10)
