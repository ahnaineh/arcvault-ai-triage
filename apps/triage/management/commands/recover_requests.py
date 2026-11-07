import time
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.intake.service import dispatch
from apps.triage.models import Request


def recover():
    now = timezone.now()
    eligible = Q(status__in=['pending', 'retrying']) & (Q(next_attempt_at__isnull=True) | Q(next_attempt_at__lte=now))
    expired = Q(status='processing') & (Q(lease_until__isnull=True) | Q(lease_until__lte=now))
    ids = list(Request.objects.filter(eligible | expired).order_by('received_at').values_list('pk', flat=True)[:100])
    for pk in ids:
        with transaction.atomic():
            row = Request.objects.select_for_update().get(pk=pk)
            if row.status == 'processing':
                if row.lease_until and row.lease_until > now:
                    continue
                row.attempts.filter(completed_at__isnull=True).update(completed_at=now, error='worker_interrupted')
                row.owner = None
                row.lease_until = None
                row.status = 'retrying'
            elif row.status not in ('pending', 'retrying'):
                continue
            if row.next_attempt_at and row.next_attempt_at > now:
                continue
            if row.attempts.count() >= 3:
                row.status = 'failed'
                row.error = 'attempt_budget_exhausted'
                row.save()
                continue
            row.next_attempt_at = now + timedelta(seconds=10)
            row.save()
        # Publish outside the transaction. A crash here is retried after ten seconds.
        dispatch(pk, countdown=10)


class Command(BaseCommand):
    help = 'Recover durable queued requests; --loop runs the runtime scanner.'

    def add_arguments(self, parser):
        parser.add_argument('--loop', action='store_true')

    def handle(self, *args, **options):
        while True:
            recover()
            if not options['loop']:
                return
            time.sleep(5)
