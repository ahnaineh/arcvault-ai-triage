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
