"""Freeze and run assistant-authored holdout expectations; dry-run by default."""
import json
import os
import re
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.triage.acceptance import Runner, atomic_export, digest, money
from apps.triage.policy import QUEUES, decide_projection
from apps.triage.providers.openai_provider import ArtifactIdentity, BoundedOpenAIAdapter
from apps.triage.schemas import Entity, Signals


def validate(cases):
    if len(cases) != 8 or len({c['id'] for c in cases}) != 8:
        raise ValueError('Eight distinct cases required')
    from evals.score import load
    normalized = lambda message: ' '.join(message.split()).casefold()
    messages = set()
    old = {normalized(c['message']) for c in load()}
    for c in cases:
        message = c['message']
        if not isinstance(message, str) or not message.strip():
            raise ValueError('message')
        key = normalized(message)
        if key in messages or key in old:
            raise ValueError('duplicate message')
        messages.add(key)
        if c['source'] not in ('Web Form', 'Email', 'Support Portal'):
            raise ValueError('source')
        status, amount = c['billing_status'], c['reported_overcharge']
        if status not in ('not_applicable', 'unresolved', 'comparable_usd'):
            raise ValueError('billing_status')
        if status == 'comparable_usd':
            if not isinstance(amount, str) or not re.fullmatch(r'-?[0-9]+(?:\.[0-9]+)?', amount):
                raise ValueError('reported_overcharge')
        elif amount is not None:
            raise ValueError('inconsistent billing annotation')
        for key in ('source', 'scenario_family', 'summary_required_facts',
                    'summary_forbidden_facts', 'rationale', 'review_status'):
            if not c[key]:
                raise ValueError(key)
        if not isinstance(c['required_entities'], list):
            raise TypeError('entities')
        Signals.model_validate({k: {'value': v, 'evidence': []} for k, v in c['expected_signals'].items()})
        for entity in c['required_entities']:
            Entity.model_validate(entity)
            if entity['evidence'] not in c['message']:
                raise ValueError('entity evidence')
        for category in c['acceptable_categories']:
            if category not in QUEUES:
                raise ValueError('category')
            expected = decide_projection(category=category, confidence=1,
                **c['expected_signals'], billing_status=c['billing_status'],
                reported_overcharge=c['reported_overcharge'])
            if c['expected_policy'] != expected:
                raise ValueError('policy mismatch')
        if not c['acceptable_categories'] or not c['acceptable_priorities'] or any(
                p not in ('Low', 'Medium', 'High') for p in c['acceptable_priorities']):
            raise ValueError('labels')


class Command(BaseCommand):
    def add_arguments(self, parser):
        for name in ('dataset', 'config', 'run-dir'):
            parser.add_argument('--' + name, required=True)
        parser.add_argument('--execute', action='store_true')

    def handle(self, *args, **options):
        import fcntl
        directory = Path(options['run_dir'])
        directory.mkdir(parents=True, exist_ok=True)
        with (directory / 'holdout.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            return self.run_locked(options)

    def run_locked(self, options):
        cases = json.loads(Path(options['dataset']).read_text())
        validate(cases)
        config = json.loads(Path(options['config']).read_text())
        execute = options['execute']
        if execute and config.get('illustrative', False):
            raise CommandError('Illustrative configuration cannot execute')
        if execute:
            try:
                for field in ('budget', 'project_budget', 'input_price_per_million',
                              'output_price_per_million'):
                    money(config[field])
                if money(config['budget']) <= 0 or money(config['budget']) > money(config['project_budget']):
                    raise ValueError('Task budget exceeds project budget or is not positive')
                for field in ('input_token_bound', 'output_token_cap'):
                    if type(config.get(field)) is not int or config[field] <= 0:
                        raise ValueError('Positive integer token bounds required')
                if config['output_token_cap'] > 128000:
                    raise ValueError('Output cap exceeds limit')
                history = config['reconciled_history']
                if not history.get('evidence'):
                    raise ValueError('History evidence required')
                for field in ('known_cost', 'unknown_reservation'):
                    money(history[field])
            except (KeyError, TypeError, ValueError, ArithmeticError) as exc:
                raise CommandError(f'Invalid execution configuration: {exc}') from exc
        config['benchmark'] = True
        provider = ArtifactIdentity(prompt_version=config.get('prompt_version'))
        identity = provider.inference_identity() | {'dataset': digest(cases), 'config': digest(config),
            'execution': {str(p): digest(p.read_text())
                          for root in ('apps/triage', 'evals')
                          for p in sorted(Path(root).rglob('*.py'))}}
        directory = Path(options['run_dir'])
        if execute and (directory.resolve() == Path('/tmp') or Path('/tmp') in directory.resolve().parents):
            raise CommandError('Execute requires persistent storage')
        directory.mkdir(parents=True, exist_ok=True)
        manifest = directory / 'holdout.identity.json'
        if manifest.exists() and json.loads(manifest.read_text()) != identity:
            raise CommandError('Frozen identity mismatch')
        atomic_export(manifest, identity)
        if execute:
            if not config.get('reconciled_history', {}).get('evidence') or not config.get('budget'):
                raise CommandError('Reconciled history and budget required')
            import openai
            provider = BoundedOpenAIAdapter(client=openai.OpenAI(api_key=os.environ['OPENAI_API_KEY']), config=config, prompt_version=config.get('prompt_version'))
        # Ephemeral dry-run storage is explicitly allowed; spending remains persistent.
        runner = Runner(directory, config, allow_ephemeral=not execute, terminal_provider_failures=True)
        result = runner.run([{'sample_id': c['id'], 'source': c['source'], 'message': c['message']}
                             for c in cases], provider, execute=execute)
        if execute:
            from evals.export_adapter import adapt
            from evals.score import score
            predictions = adapt(result, cases)
            atomic_export(directory / 'holdout.exports.json', result)
            atomic_export(directory / 'holdout.predictions.json', predictions)
            atomic_export(directory / 'holdout.score.json', score(cases, predictions))
        reserve = (money(config['input_price_per_million']) * config['input_token_bound'] +
                   money(config['output_price_per_million']) * config['output_token_cap']) / 1000000
        self.stdout.write(json.dumps({'result': result, 'cases': len(cases),
            'reservation_per_case': str(reserve), 'reservation_all_cases': str(reserve * len(cases)),
            'pricing': 'historical configured prices; not current prices',
            'labels': 'assistant authored, unevaluated; human summary review required'}))
