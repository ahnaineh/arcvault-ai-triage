import json
from unittest.mock import Mock
import pytest
from openai.types.responses import Response
from apps.triage.providers.openai_provider import OpenAIProvider, ProviderError

def envelope(**changes):
    data = dict(id='resp_test', created_at=0, model='mock-model', object='response',
        status='completed', output=[], parallel_tool_calls=False, tool_choice='auto',
        tools=[], usage=None)
    data.update(changes)
    return Response.model_validate(data)

def test_request_and_missing_output():
    client = Mock()
    client.with_options.return_value = client
    client.responses.create.return_value = envelope()
    provider = OpenAIProvider(client=client, model='configured-model')
    with pytest.raises(ProviderError, match='provider_invalid') as caught:
        provider.analyze('untrusted message')
    assert caught.value.usage is None
    client.with_options.assert_called_once_with(max_retries=0, timeout=30)
    args = client.responses.create.call_args.kwargs
    assert args['input'] == [{'role':'user','content':'untrusted message'}]
    assert 'untrusted message' not in args['instructions']
    assert args['text']['format']['strict'] is True
    assert args['store'] is False
    client.responses.create.assert_called_once()

@pytest.mark.parametrize('status,output,code', [
    ('incomplete', [], 'provider_incomplete'),
    ('completed', [{'id':'msg_1','type':'message','role':'assistant','status':'completed',
                    'content':[{'type':'refusal','refusal':'private reason'}]}], 'provider_refusal'),
    ('completed', [{'id':'msg_1','type':'message','role':'assistant','status':'completed',
                    'content':[{'type':'output_text','text':'{}','annotations':[]}]}], 'provider_invalid')])
def test_failures(status, output, code):
    client=Mock(); client.with_options.return_value=client
    client.responses.create.return_value=envelope(status=status,output=output)
    with pytest.raises(ProviderError, match=code) as caught:
        OpenAIProvider(client=client,model='mock').analyze('message')
    assert not caught.value.retryable
    assert caught.value.latency_ms >= 0

def test_success_usage():
    data=dict(category='Technical Question',priority='Low',confidence=.9,core_issue='Usage question.',entities=[],urgency={'level':'Unknown','evidence':[]},signals={k:{'value':False,'evidence':[]} for k in ['active_service_outage','insufficient_information','conflicting_intents']},billing_comparison=None,summary_sentences=['Customer asks about usage.','No further context supplied.'])
    client=Mock(); client.with_options.return_value=client
    client.responses.create.return_value=envelope(output=[{'id':'msg_1','type':'message','role':'assistant','status':'completed','content':[{'type':'output_text','text':json.dumps(data),'annotations':[]}]}],usage={'input_tokens':10,'output_tokens':20,'total_tokens':30,'input_tokens_details':{'cached_tokens':0,'cache_write_tokens':0},'output_tokens_details':{'reasoning_tokens':0}})
    result=OpenAIProvider(client=client,model='mock').analyze('usage?')
    assert result.usage['total_tokens']==30
    assert result.analysis.category=='Technical Question'
    assert len(result.prompt_sha256)==64
