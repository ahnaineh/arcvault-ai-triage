import json
from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.intake.sample_data import samples
from apps.triage.models import Attempt, Request, Result


@pytest.mark.django_db
def test_samples_repeat_and_export():
    with patch('apps.intake.service.dispatch'):
        call_command('load_samples', principal='samples', stdout=StringIO())
        call_command('load_samples', principal='samples', stdout=StringIO())
    assert Request.objects.count() == 5
    output = StringIO()
    with pytest.raises(CommandError):
        call_command('export_samples', principal='samples', stdout=output)
    assert output.getvalue() == ''
    expected = []
    for item in samples():
        row = Request.objects.get(idempotency_key=f'assessment-v1:{item["sample_id"]}')
        assert (row.source, row.message) == (item['source'], item['message'])
        attempt = Attempt.objects.create(request=row)
        record = {'original_message': row.message, 'source': row.source}
        Result.objects.create(request=row, attempt=attempt, record=record)
        row.status = 'completed'
        row.save()
        expected.append(record)
    call_command('export_samples', principal='samples', stdout=output)
    assert json.loads(output.getvalue()) == expected
    with patch('apps.intake.service.dispatch'):
        call_command('load_samples', principal='other', stdout=StringIO())
    assert Request.objects.count() == 10


@pytest.mark.django_db
@pytest.mark.parametrize('invalid', [None, 'result', 'source', 'message'])
def test_pipeline_export(invalid):
    from types import SimpleNamespace

    from apps.triage.tasks import process
    from tests.test_backend import analysis

    with patch('apps.intake.service.dispatch'):
        call_command('load_samples', principal='pipeline', stdout=StringIO())
    expected = []
    for item in samples():
        row = Request.objects.get(principal='pipeline',
                                  idempotency_key=f'assessment-v1:{item["sample_id"]}')
        output = SimpleNamespace(analysis=analysis(), model='mock', prompt_version='v1',
                                 schema_version='v1', latency_ms=12, usage=None)
        with patch('apps.triage.tasks.get_provider') as provider:
            provider.return_value.analyze.return_value = output
            process(str(row.pk))
        row.refresh_from_db()
        assert row.status == 'completed'
        record = row.accepted_result.record
        assert record['request']['message'] == item['message']
        assert record['request']['source'] == item['source']
        assert {'schema_version', 'request', 'analysis', 'decision'} <= record.keys()
        expected.append(record)
    if invalid == 'result':
        row.accepted_result.delete()
    elif invalid:
        setattr(row, invalid, 'mismatched')
        row.save()
    exported = StringIO()
    if invalid:
        with pytest.raises(CommandError):
            call_command('export_samples', principal='pipeline', stdout=exported)
        assert exported.getvalue() == ''
    else:
        call_command('export_samples', principal='pipeline', stdout=exported)
        assert json.loads(exported.getvalue()) == expected
