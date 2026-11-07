"""Canonical application and acceptance export record."""
from .policy import decide


def build_record(*, request, analysis, output, completed_at, attempt_id, attempts):
    return {'schema_version': '1.0', 'request': request,
            'analysis': analysis.model_dump(mode='json'), 'decision': decide(analysis),
            'summary': ' '.join(analysis.summary_sentences), 'provenance': {
                'model': output.model, 'prompt_version': output.prompt_version,
                'prompt_sha256': getattr(output, 'prompt_sha256', None), 'schema_sha256': getattr(output, 'schema_sha256', None),
                'schema_version': output.schema_version, 'policy_version': '1.1',
                'completed_at': completed_at, 'accepted_attempt_id': attempt_id},
            'processing': {'attempts': attempts, 'estimated_cost': None, 'unknown_cost': True},
            'review': None}
