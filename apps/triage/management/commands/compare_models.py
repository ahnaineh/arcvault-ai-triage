"""Frozen reused-set comparison through the existing serial acceptance runner."""
import json
import os
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.triage.acceptance import Runner, accounted, atomic_export, digest, money
from apps.triage.providers.openai_provider import ArtifactIdentity, BoundedOpenAIAdapter
from evals.export_adapter import adapt
from evals.score import load, score


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--run-dir', required=True)
        parser.add_argument('--execute', action='store_true')
        parser.add_argument('--accept-harness-update', action='store_true')

    def handle(self, *args, **options):
        import fcntl
        root = Path(options['run_dir'])
        root.mkdir(parents=True, exist_ok=True)
        with (root / 'comparison.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            self.compare(root, options['execute'], options['accept_harness_update'])

    def compare(self, root, execute, accept_harness_update=False):
        cases = load()
        prompt = Path('prompts/triage_v3.txt').read_text()
        identity = {'prompt': digest(prompt), 'schema': digest(Path('contracts/analysis.schema.json').read_text()),
                    'dataset': digest(cases), 'set_status': 'reused comparison set; not a fresh holdout',
                    'models': {'gpt-6-luna': 'high', 'gpt-6.1-terra': 'none'},
                    'code': {str(p): digest(p.read_text()) for d in ('apps/triage', 'evals') for p in sorted(Path(d).rglob('*.py'))}}
        freeze = root / 'freeze.json'
        if freeze.exists() and json.loads(freeze.read_text()) != identity:
            previous = json.loads(freeze.read_text())
            if not accept_harness_update or any(previous[k] != identity[k] for k in identity if k != 'code'):
                raise CommandError('Frozen comparison identity changed')
            atomic_export(root / ('harness-amendment-' + digest(previous) + '.json'),
                {'previous': previous, 'current': identity, 'reason': 'Terminal invalid responses remain failures; no retry or inference change'})
        if execute:
            atomic_export(freeze, identity)
        prior_total = money('0')
        for model, effort in identity['models'].items():
            directory = root / model
            directory.mkdir(exist_ok=True)
            config_path = directory / 'config.json'
            config = json.loads(Path('config/acceptance/benchmark.json').read_text())
            config.update(model=model, reasoning_effort=effort, output_token_cap=25000, timeout=180)
            config['reconciled_history'].update(known_cost=str(money('1.1698115') + prior_total),
                evidence='Prior original five plus 75-call benchmark: docs/evidence/benchmark-20261107/execution-summary.json; preceding comparison model journal accounted under shared lock. Both historical uncertain reservations retained.')
            if model == 'gpt-6-luna':
                config.update(input_price_per_million='1.1', output_price_per_million='5.5')
            if config_path.exists() and json.loads(config_path.read_text()) != config:
                raise CommandError('Immutable comparison accounting mismatch')
            provider = ArtifactIdentity()
            if execute:
                import openai
                provider = BoundedOpenAIAdapter(client=openai.OpenAI(api_key=os.environ['OPENAI_API_KEY']), config=config)
                provider.provider.prompt = prompt
                provider.provider.prompt_version = 'triage_v3'
                atomic_export(config_path, config)
            runner = Runner(directory, config, terminal_provider_failures=True)
            records = runner.run([{'sample_id': c['id'], 'source': c['source'], 'message': c['message']}
                                  for c in cases], provider, execute=execute)
            if execute:
                atomic_export(directory / 'exports.json', records)
                predictions = adapt(records, cases)
                atomic_export(directory / 'predictions.json', predictions)
                atomic_export(directory / 'score.json', score(cases, predictions))
                for split in ('development', 'validation', 'test', 'assessment'):
                    ids = {c['id'] for c in cases if c['split'] == split}
                    atomic_export(directory / f'{split}.score.json', score([c for c in cases if c['id'] in ids],
                        [p for p in predictions if p['id'] in ids]))
            if runner.path.exists():
                events = [json.loads(line) for line in runner.path.read_text().splitlines()]
                prior_total += accounted(events, config)[0]
            self.stdout.write(json.dumps({'model': model, 'effort': effort, 'cases': len(cases), 'execute': execute}))
