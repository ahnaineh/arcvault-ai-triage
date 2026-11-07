import json

from django.core.management.base import BaseCommand, CommandError

from apps.intake.sample_data import sample_key, samples
from apps.triage.models import Request


class Command(BaseCommand):
    help = 'Export all five completed DB records in original assessment order.'

    def add_arguments(self, parser):
        parser.add_argument('--principal', required=True)

    def handle(self, *args, **options):
        records = []
        for item in samples():
            row = Request.objects.select_related('accepted_result').filter(
                principal=options['principal'], idempotency_key=sample_key(item)).first()
            if (row is None or row.status != 'completed' or
                    row.source != item['source'] or row.message != item['message'] or
                    not hasattr(row, 'accepted_result')):
                raise CommandError(f'Sample {item["sample_id"]} missing, incomplete or mismatched')
            records.append(row.accepted_result.record)
        self.stdout.write(json.dumps(records, ensure_ascii=False, indent=2))
