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
