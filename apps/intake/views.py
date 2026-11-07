import json
import secrets

from django.conf import settings
from django.core.exceptions import RequestDataTooBig
from django.db import DatabaseError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from apps.triage.models import Request

from .service import accept


def error(code, status):
    return JsonResponse({'error': {'code': code, 'message': code.replace('_', ' '), 'fields': {}}}, status=status)


def csrf_failure(request, reason=''):
    return error('csrf_failed', 403)


def payload_error(data):
    if not isinstance(data, dict) or set(data) - {'source', 'message', 'idempotency_key'}:
        return True
    if data.get('source') not in ['Email', 'Web Form', 'Support Portal']:
        return True
    message = data.get('message')
    if not isinstance(message, str) or not message.strip() or len(message) > 20000:
        return True
    if 'idempotency_key' in data:
        key = data['idempotency_key']
        if not isinstance(key, str) or not key.strip() or len(key) > 128:
            return True
    return False


def record(row):
    return row.accepted_result.record if row.status == 'completed' else None


def protected(request, request_id=None, export=False):
    if request.method == 'POST' and request_id is None:
        if request.content_type != 'application/json':
            return error('unsupported_media_type', 415)
        try:
            body = request.body
        except RequestDataTooBig:
            return error('body_too_large', 413)
        if len(body) > 131072:
            return error('body_too_large', 413)
        try:
            data = json.loads(request.body)
        except (ValueError, UnicodeError):
            return error('invalid_json', 400)
        if payload_error(data):
            return error('invalid_payload', 400)
        try:
            row, created = accept(request.principal, data)
        except ValueError:
            return error('idempotency_conflict', 409)
        except DatabaseError:
            return error('storage_unavailable', 503)
        row.refresh_from_db()
        url = f'/api/v1/requests/{row.pk}/'
        response = JsonResponse({'id': str(row.pk), 'status': row.status, 'status_url': url,
                                 'replayed': not created}, status=202 if created else 200)
        response['Location'] = url
        return response
    if request.method != 'GET' or request_id is None:
        return error('method_not_allowed', 405)
    row = Request.objects.filter(pk=request_id).first()
    if row is None:
        return error('not_found', 404)
    if export:
        return JsonResponse(record(row)) if row.status == 'completed' else error('incomplete', 409)
    return JsonResponse({'id': str(row.pk), 'status': row.status,
        'received_at': row.received_at.isoformat(), 'updated_at': row.updated_at.isoformat(),
        'attempt_count': row.attempts.count(),
        'next_attempt_at': row.next_attempt_at.isoformat() if row.next_attempt_at else None,
        'dispatch_error': row.dispatch_error, 'error': row.error, 'result': record(row)})


@csrf_exempt
def endpoint(request, **kwargs):
    authorization = request.headers.get('Authorization')
    if authorization is not None:
        token = getattr(settings, 'INTAKE_BEARER_TOKEN', '')
        if not token or not secrets.compare_digest(authorization.encode(), ('Bearer ' + token).encode()):
            return error('invalid_credentials', 401)
        request.principal = 'service'
        return protected(request, **kwargs)
    if not request.user.is_authenticated:
        return error('authentication_required', 401)
    request.principal = f'user:{request.user.pk}'
    return csrf_protect(protected)(request, **kwargs)
