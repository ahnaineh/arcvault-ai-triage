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
    def __init__(self, *, client, model: str, timeout: float = 30):
        if not model.strip() or not math.isfinite(timeout) or timeout <= 0:
            raise ProviderError('provider_config')
        self.client = client.with_options(max_retries=0, timeout=timeout)
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
                model=self.model, instructions=self.prompt,
                input=[{'role': 'user', 'content': message}], store=False,
                text={'format': {'type': 'json_schema', 'name': 'arcvault_analysis',
                                 'strict': True, 'schema': json.loads(self.schema_text)}})
        except (openai.AuthenticationError, openai.PermissionDeniedError):
            raise fail('provider_auth') from None
        except (openai.APIConnectionError, openai.RateLimitError):
            raise fail('provider_transient') from None
        except openai.APIStatusError as exc:
            raise fail('provider_transient' if exc.status_code >= 500 or exc.status_code == 408 else 'provider_config') from None
        try:
            if response.usage is not None:
                usage = response.usage.model_dump(mode='json')
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
            return ProviderResult(analysis, response.model, self.model, 'triage_v1', '1.0',
                hashlib.sha256(self.prompt.encode()).hexdigest(),
                hashlib.sha256(self.schema_text.encode()).hexdigest(),
                (time.monotonic()-started)*1000, usage)
        except (ValueError, TypeError, AttributeError, ValidationError):
            raise fail('provider_invalid') from None
