import json
from unittest.mock import Mock, patch

import pytest
from openai.types.responses import Response

from apps.triage.models import Request
from apps.triage.providers.openai_provider import OpenAIProvider
from apps.triage.tasks import process
from tests.test_backend import analysis


@pytest.mark.django_db
@pytest.mark.parametrize('valid',[True,False])
def test_composed(valid):
    client=Mock(); client.with_options.return_value=client
    client.responses.create.return_value=Response.model_validate({'id': 'r','created_at': 0,'model': 'mock','object': 'response','status': 'completed','parallel_tool_calls': False,'tool_choice': 'auto','tools': [],'usage': None,'output': [{'id': 'm','type': 'message','role': 'assistant','status': 'completed','content': [{'type': 'output_text','text': json.dumps(analysis().model_dump(mode='json')) if valid else '{}','annotations': []}]}]})
    adapter=OpenAIProvider(client=client,model='mock')
    row=Request.objects.create(principal='service',source='Email',message='usage?')
    with patch('apps.triage.tasks.get_provider',return_value=adapter): process(str(row.pk))
    row.refresh_from_db()
    assert row.status == ('completed' if valid else 'failed')
    assert client.responses.create.call_count==1
    if not valid: assert row.error=='provider_invalid'
