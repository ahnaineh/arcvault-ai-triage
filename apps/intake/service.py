from django.db import transaction

from apps.triage.models import Request


def dispatch(request_id, countdown=0):
    from apps.triage.tasks import process
    try:
        process.apply_async(args=[str(request_id)], countdown=countdown, retry=False)
    except Exception:  # noqa: BLE001 - persist broker failure
        Request.objects.filter(pk=request_id).exclude(status='completed').update(dispatch_error='dispatch_failed')
    else:
        Request.objects.filter(pk=request_id).update(dispatch_error=None)


def accept(principal, payload):
    with transaction.atomic():
        key = payload.get('idempotency_key')
        if key is None:
            row = Request.objects.create(principal=principal, **payload)
            created = True
        else:
            row, created = Request.objects.get_or_create(principal=principal, idempotency_key=key,
                defaults={'source': payload['source'], 'message': payload['message']})
        if row.source != payload['source'] or row.message != payload['message']:
            raise ValueError('idempotency_conflict')
        if created:
            transaction.on_commit(lambda: dispatch(row.pk))
    return row, created
