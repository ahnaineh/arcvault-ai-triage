"""Persistent, explicitly budgeted acceptance execution."""
import json
import os
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.intake.sample_data import samples
from apps.triage.acceptance import Runner, money
from apps.triage.providers.openai_provider import BoundedOpenAIAdapter


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--run-dir', required=True)
        parser.add_argument('--config', required=True)
        parser.add_argument('--execute', action='store_true')

    def handle(self, *args, **options):
        config = json.loads(Path(options['config']).read_text())
        runner = Runner(options['run_dir'], config)
        provider = None
        if options['execute']:
            history = config.get('reconciled_history', {})
            if not history.get('evidence') or not history.get('provenance'):
                raise CommandError('Explicit history evidence and provenance required')
            for field in ('known_cost', 'unknown_reservation'):
                money(history[field])
            if config.get('model') != 'gpt-6.1-terra':
                raise CommandError('Terra configuration required')
            if not config.get('official_price_source', '').startswith(('https://openai.com/', 'https://developers.openai.com/')):
                raise CommandError('Official pricing binding required')
            if not 0 < config.get('output_token_cap', 0) <= 128000:
                raise CommandError('Explicit output cap required')
            if money(config['budget']) > money(config['project_budget']):
                raise CommandError('Task budget exceeds project budget')
            import openai
            provider = BoundedOpenAIAdapter(client=openai.OpenAI(api_key=os.environ['OPENAI_API_KEY']), config=config)
            provider.preflight([case['message'] for case in samples()], config)

            def persist(response):
                # Whitelist model content and accounting, never HTTP headers or request credentials.
                payload = {'id': str(response.id)[:256], 'model': str(response.model)[:256],
                           'status': str(response.status)[:64],
                           'usage': response.usage.model_dump(mode='json') if response.usage else None,
                           'output': response.model_dump(mode='json').get('output', [])}
                encoded = json.dumps(payload)
                limit = config['output_token_cap'] * 64 + 65536
                if len(encoded.encode()) > limit:
                    payload['output'] = encoded[:limit]
                    payload['truncated'] = True
                runner.append({'state': 'raw_response', 'payload': payload})

            provider.provider.raw_sink = persist
        result = runner.run(samples(), provider, execute=options['execute'])
        self.stdout.write(json.dumps(result))
