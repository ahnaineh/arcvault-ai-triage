from datetime import timedelta
from math import ceil

from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .export import build_record
from .models import Attempt, Request, Result
from .policy import decide
from .schemas import validate_analysis


def get_provider():
    from openai import OpenAI

    from .providers.openai_provider import OpenAIProvider
    return OpenAIProvider(client=OpenAI(), model=settings.OPENAI_MODEL, timeout=30,
                          prompt_version=settings.OPENAI_PROMPT_VERSION)


@shared_task
def process(request_id):
    with transaction.atomic():
        row = Request.objects.select_for_update().get(pk=request_id)
        if row.status not in ('pending', 'retrying'):
            return
        if row.next_attempt_at and row.next_attempt_at > timezone.now():
            from apps.intake.service import dispatch
            countdown = max(1, ceil((row.next_attempt_at - timezone.now()).total_seconds()))
            transaction.on_commit(lambda: dispatch(row.pk, countdown=countdown))
            return
        row.status = 'processing'
        row.next_attempt_at = None
        row.dispatch_error = None
        row.save()
        attempt = Attempt.objects.create(request=row)
    try:
        output = get_provider().analyze(row.message)
        analysis = validate_analysis(output.analysis.model_dump(mode='json'), row.message)
        decide(analysis)
    except Exception as exc:  # noqa: BLE001 - sanitize all processing failures
        code = getattr(exc, 'code', '')
        safe = code if code in {'provider_transient', 'provider_auth', 'provider_config', 'provider_refusal', 'provider_incomplete', 'provider_invalid'} else 'processing_failed'
        with transaction.atomic():
            row = Request.objects.select_for_update().get(pk=request_id)
            attempt.latency_ms = getattr(exc, 'latency_ms', None)
            attempt.usage = getattr(exc, 'usage', None)
            attempt.error = safe
            attempt.completed_at = timezone.now()
            attempt.save()
            retry = safe == 'provider_transient' and row.attempts.count() < 3
            row.status = 'retrying' if retry else 'failed'
            row.error = safe
            row.next_attempt_at = timezone.now() + timedelta(seconds=10) if retry else None
            row.save()
            if retry:
                from apps.intake.service import dispatch
                transaction.on_commit(lambda: dispatch(row.pk, countdown=10))
        return
    with transaction.atomic():
        row = Request.objects.select_for_update().get(pk=request_id)
        attempt.completed_at = timezone.now()
        attempt.latency_ms = output.latency_ms
        attempt.usage = output.usage
        attempt.save()
        attempts = list(row.attempts.order_by('pk').values('id', 'error', 'latency_ms', 'usage'))
        result = build_record(request={'id': str(row.pk), 'source': row.source,
            'message': row.message, 'received_at': row.received_at.isoformat()},
            analysis=analysis, output=output, completed_at=attempt.completed_at.isoformat(),
            attempt_id=attempt.pk, attempts=attempts)
        Result.objects.create(request=row, attempt=attempt, record=result)
        row.status = 'completed'
        row.error = None
        row.save()
