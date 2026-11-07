"""One synchronous Responses request per pipeline-owned attempt; no credential lookup."""
import hashlib
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path

import openai
from pydantic import ValidationError

from apps.triage.schemas import Analysis, validate_analysis

ROOT = Path(__file__).resolve().parents[3]

def artifact_identity(prompt=None, schema=None):
    if prompt is None:
        prompt = (ROOT / 'prompts/triage_v1.txt').read_text()
    if schema is None:
        schema = (ROOT / 'contracts/analysis.schema.json').read_text()
    return {'prompt': hashlib.sha256(prompt.encode()).hexdigest(),
            'schema': hashlib.sha256(schema.encode()).hexdigest()}


class ArtifactIdentity:
    def inference_identity(self):
        return artifact_identity()


MAX_MODEL_BYTES = 1048576


def safe_usage(value):
    """Persist only bounded accounting counters."""
    if hasattr(value, 'model_dump'):
        value = value.model_dump(mode='json')
    if not isinstance(value, dict):
        return None
    return {key: value[key] for key in ('input_tokens', 'output_tokens', 'total_tokens')
            if type(value.get(key)) is int and 0 <= value[key] <= 10**12}


def response_evidence(response):
    parts = [part.text for item in response.output if item.type == 'message'
             for part in item.content if part.type == 'output_text']
    size = sum(len(text.encode()) for text in parts)
    oversized = size > MAX_MODEL_BYTES or len(parts) > 16
    return {'id': str(response.id)[:256], 'model': str(response.model)[:256],
            'status': str(response.status)[:64], 'usage': safe_usage(response.usage),
            'output_text': [] if oversized else parts,
            'output_bytes': size, 'truncated': oversized,
            'metadata_truncated': any(len(str(value)) > limit for value, limit in
                                      ((response.id, 256), (response.model, 256),
                                       (response.status, 64)))}


class ProviderError(Exception):
    """Safe public failure. Never contains provider text or customer content."""
    def __init__(self, code, *, latency_ms=0, usage=None):
        self.code = code
        self.retryable = code == 'provider_transient'
        self.latency_ms = latency_ms
        self.usage = usage
        super().__init__(code)

@dataclass(frozen=True)
class ProviderResult:
    analysis: Analysis
    model: str
    requested_model: str
    prompt_version: str
    schema_version: str
    prompt_sha256: str
    schema_sha256: str
    latency_ms: float
    usage: dict | None

class OpenAIProvider:
    def __init__(self, *, client, model: str, timeout: float = 30, max_output_tokens: int = 4096):
        if not model.strip() or not math.isfinite(timeout) or timeout <= 0:
            raise ProviderError('provider_config')
        if type(max_output_tokens) is not int or max_output_tokens <= 0 or (model == 'gpt-6.1-terra' and max_output_tokens > 128000):
            raise ProviderError('provider_config')
        self.max_output_tokens = max_output_tokens
        self.client = client.with_options(max_retries=0, timeout=timeout)
        self.raw_sink = None
        self.prompt_version = 'triage_v1'
        self.model = model
        self.prompt = (ROOT / 'prompts/triage_v1.txt').read_text()
        self.schema_text = (ROOT / 'contracts/analysis.schema.json').read_text()

    def analyze(self, message: str) -> ProviderResult:
        started = time.monotonic()
        usage = None
        def fail(code):
            return ProviderError(code, latency_ms=(time.monotonic()-started)*1000, usage=usage)
        try:
            response = self.client.responses.create(
                model=self.model, max_output_tokens=self.max_output_tokens, instructions=self.prompt,
                input=[{'role': 'user', 'content': message}], store=False,
                **({'reasoning': {'effort': 'none'}} if self.model == 'gpt-6.1-terra' else {}),
                text={'format': {'type': 'json_schema', 'name': 'arcvault_analysis',
                                 'strict': True, 'schema': json.loads(self.schema_text)}})
        except openai.APIConnectionError:
            raise fail('provider_transient') from None
        except openai.APIStatusError as exc:
            body = exc.body if isinstance(exc.body, dict) else {}
            usage = safe_usage(body.get('usage'))
            if self.raw_sink is not None:
                try:
                    self.raw_sink({'status_code': exc.status_code, 'usage': usage,
                                   'state': 'http_failure'})
                except OSError as write_error:
                    write_error.usage = usage
                    raise write_error from None
            code = ('provider_auth' if exc.status_code in (401, 403) else
                    'provider_transient' if exc.status_code >= 500 or exc.status_code in (408, 429)
                    else 'provider_config')
            raise fail(code) from None
        try:
            usage = safe_usage(response.usage)
            evidence = response_evidence(response)
            if self.raw_sink is not None:
                try:
                    self.raw_sink(evidence)
                except OSError as exc:
                    exc.usage = usage
                    raise
            if evidence['truncated']:
                raise fail('provider_oversized')
            if any(part.type == 'refusal' for item in response.output
                   if item.type == 'message' for part in item.content):
                raise fail('provider_refusal')
            if response.status != 'completed':
                raise fail('provider_incomplete')
            parts = [part.text for item in response.output if item.type == 'message'
                     for part in item.content if part.type == 'output_text']
            if len(parts) != 1:
                raise fail('provider_invalid')
            analysis = validate_analysis(json.loads(parts[0]), message)
            return ProviderResult(analysis, str(response.model)[:256], self.model, self.prompt_version, '1.0',
                hashlib.sha256(self.prompt.encode()).hexdigest(),
                hashlib.sha256(self.schema_text.encode()).hexdigest(),
                (time.monotonic()-started)*1000, usage)
        except (ValueError, TypeError, AttributeError, ValidationError):
            raise fail('provider_invalid') from None


class BoundedOpenAIAdapter:
    """Bind a runner to exact configuration and an externally proven input bound.

    The verifier must cover Responses message framing, instructions and JSON schema,
    not just customer text. No default heuristic is accepted as a proof.
    """
    enforces_bounds = True

    def __init__(self, *, client, config, verify_input_bound=None):
        self.config = json.loads(json.dumps(config))
        self.verify_input_bound = verify_input_bound or self.maximum_input_bound
        self.provider = OpenAIProvider(
            client=client, model=config['model'], timeout=config['timeout'],
            max_output_tokens=config['output_token_cap'])

    def inference_identity(self):
        return artifact_identity(self.provider.prompt, self.provider.schema_text)

    @staticmethod
    def maximum_input_bound(*, model, bound, **kwargs):
        return model == 'gpt-6.1-terra' and bound >= 1050000

    def preflight(self, messages, config):
        if config != self.config:
            raise ValueError('Adapter configuration mismatch')
        if self.provider.model == 'gpt-6.1-terra':
            from decimal import Decimal

            from apps.triage.acceptance import money
            if (money(config['input_price_per_million']) < Decimal(11) or
                    money(config['output_price_per_million']) < Decimal('16.5')):
                raise ValueError('Maximum context requires conservative premium prices')
        for message in messages:
            if self.verify_input_bound(
                model=self.provider.model, instructions=self.provider.prompt,
                schema=json.loads(self.provider.schema_text), message=message,
                bound=config['input_token_bound']) is not True:
                raise ValueError('Input reservation cannot be verified')

    def __call__(self, message, config):
        self.preflight([message], config)
        return self.provider.analyze(message)
