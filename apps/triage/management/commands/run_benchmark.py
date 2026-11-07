"""Serial benchmark using the acceptance journal, canonical exports and scorer."""
import json
import os
import subprocess
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.triage.acceptance import Runner, atomic_export, digest
from apps.triage.providers.openai_provider import (
    ArtifactIdentity,
    BoundedOpenAIAdapter,
    prompt_text,
    selected_prompt_version,
)
from evals.export_adapter import adapt
from evals.score import load, score


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--run-dir', required=True)
        parser.add_argument('--config', required=True)
        parser.add_argument('--phase', required=True, choices=['baseline', 'development', 'validation', 'test', 'assessment', 'comparison'])
        parser.add_argument('--prompt', help='Explicit repository versioned prompt path (legacy compatibility)')
        parser.add_argument('--prompt-version', choices=['triage_v1', 'triage_v2', 'triage_v3', 'triage_v4'])
        parser.add_argument('--freeze', action='store_true')
        parser.add_argument('--execute', action='store_true')

    def handle(self, *args, **options):
        import fcntl
        directory = Path(options['run_dir'])
        directory.mkdir(parents=True, exist_ok=True)
        with (directory / 'benchmark.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            return self.run_locked(options, directory)

    def run_locked(self, options, directory):
        config = json.loads(Path(options['config']).read_text())
        if not config.get('benchmark') or config['model'] != 'gpt-6.1-terra' or config['budget'] != '83':
            raise CommandError('Explicit Terra benchmark configuration with project ceiling required')
        phase = options['phase']
        split = 'development' if phase == 'baseline' else phase
        cases = [c for c in load() if phase == 'comparison' or c['split'] == split]
        prerequisite = {'development': 'baseline', 'validation': 'development', 'test': 'validation', 'assessment': 'test'}.get(phase)
        if options['execute'] and prerequisite and not (directory / f'{prerequisite}.exports.json').exists():
            raise CommandError('Complete preceding phase first')
        version = selected_prompt_version(options['prompt_version'] or (
            Path(options['prompt']).stem if options['prompt'] else config.get('prompt_version')))
        if options['prompt'] and Path(options['prompt']).read_text() != prompt_text(version):
            raise CommandError('Prompt path must contain the selected versioned artifact')
        # Phase-specific inference identity must not reset shared accounting.
        if phase == 'comparison':
            config['prompt_version'] = version
        else:
            config.pop('prompt_version', None)
        prompt = prompt_text(version)
        identity = {'prompt': digest(prompt), 'schema': digest(Path('contracts/analysis.schema.json').read_text()),
                    'dataset': digest(load()), 'model': config['model'],
                    'code_files': {str(p): digest(p.read_text()) for root in ('apps/triage', 'evals') for p in sorted(Path(root).rglob('*.py'))},
                    'set_status': 'reused comparison set; not a fresh holdout' if phase == 'comparison' else 'development/validation/frozen-test protocol',
                    'code': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()}
        manifest = directory / f'{phase}.manifest.json'
        if manifest.exists() and not options['freeze'] and json.loads(manifest.read_text()) != identity:
            raise CommandError('Immutable phase identity changed')
        freeze = directory / 'freeze.json'
        if phase in ('test', 'assessment') and (not freeze.exists() or json.loads(freeze.read_text()) != identity):
            raise CommandError('Frozen identity required before final test')
        if options['freeze']:
            if phase != 'validation' or not (directory / 'validation.exports.json').exists():
                raise CommandError('Complete validation before freeze')
            if freeze.exists() and json.loads(freeze.read_text()) != identity:
                raise CommandError('Already frozen')
            validated = json.loads(manifest.read_text())
            if any(validated[k] != identity[k] for k in ('prompt', 'schema', 'dataset', 'model')):
                raise CommandError('Validated inference identity changed')
            atomic_export(freeze, identity)
            self.stdout.write('Frozen validated inference and current code identity')
            return
        provider = ArtifactIdentity(prompt_version=version)
        if options['execute']:
            import openai
            provider = BoundedOpenAIAdapter(client=openai.OpenAI(api_key=os.environ['OPENAI_API_KEY']), config=config, prompt_version=version)
            atomic_export(manifest, identity)
        # All phases share one exclusive, immutable accounting journal.
        runner = Runner(directory, config, terminal_provider_failures=phase == 'comparison')
        records = runner.run([{'sample_id': phase + ':' + c['id'], 'source': c['source'],
                               'message': c['message']} for c in cases], provider, execute=options['execute'])
        if options['execute']:
            atomic_export(directory / f'{phase}.exports.json', records)
            predictions = adapt(records, cases)
            atomic_export(directory / f'{phase}.predictions.json', predictions)
            atomic_export(directory / f'{phase}.score.json', score(cases, predictions))
        self.stdout.write(json.dumps({'phase': phase, 'cases': len(cases), 'execute': options['execute']}))
