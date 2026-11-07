from django.core.management.base import BaseCommand

from apps.intake.sample_data import sample_key, samples
from apps.intake.service import accept


class Command(BaseCommand):
    help = 'Submit the five original assessment messages through normal intake.'

    def add_arguments(self, parser):
        parser.add_argument('--principal', required=True)

    def handle(self, *args, **options):
        for item in samples():
            row, created = accept(options['principal'], {
                'source': item['source'], 'message': item['message'],
                'idempotency_key': sample_key(item),
            })
            self.stdout.write(f'{item["sample_id"]} {row.pk} {"created" if created else "replayed"}')
