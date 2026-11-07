from unittest.mock import Mock

import pytest

from apps.triage.providers.openai_provider import BoundedOpenAIAdapter


def test_unverifiable_input_never_invokes():
    client = Mock()
    config = {'model': 'mock', 'timeout': 12, 'output_token_cap': 100,
              'input_token_bound': 200}
    adapter = BoundedOpenAIAdapter(client=client, config=config,
                                   verify_input_bound=lambda **kwargs: False)
    with pytest.raises(ValueError, match='cannot be verified'):
        adapter('message', config)
    client.with_options.return_value.responses.create.assert_not_called()


def test_config_change_rejected():
    client = Mock()
    config = {'model': 'mock', 'timeout': 12, 'output_token_cap': 100,
              'input_token_bound': 200}
    adapter = BoundedOpenAIAdapter(client=client, config=config,
                                   verify_input_bound=lambda **kwargs: True)
    with pytest.raises(ValueError, match='configuration mismatch'):
        adapter('message', {**config, 'output_token_cap': 101})


@pytest.mark.parametrize('input_price,output_price', [('2', '7.5'), ('NaN', '17'), ('11', 'Infinity')])
def test_fallback_rejects_unsafe_prices(input_price, output_price):
    config = {'model': 'gpt-6.1-terra', 'timeout': 12, 'output_token_cap': 4096,
              'input_token_bound': 1050000, 'input_price_per_million': input_price,
              'output_price_per_million': output_price}
    client = Mock()
    adapter = BoundedOpenAIAdapter(client=client, config=config)
    with pytest.raises(ValueError):
        adapter.preflight(['hello'], config)
    client.with_options.return_value.responses.create.assert_not_called()


def test_full_context_fallback():
    config = {'model': 'gpt-6.1-terra', 'timeout': 12, 'output_token_cap': 4096,
              'input_token_bound': 1050000, 'input_price_per_million': '11',
              'output_price_per_million': '16.5'}
    adapter = BoundedOpenAIAdapter(client=Mock(), config=config)
    adapter.preflight(['hello'], config)
    assert not adapter.maximum_input_bound(model='mock', bound=1050000)
    assert not adapter.maximum_input_bound(model='gpt-6.1-terra', bound=1049999)
