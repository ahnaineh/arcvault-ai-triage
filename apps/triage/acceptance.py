"""Durable, offline-first acceptance journal. No credential discovery or live adapter."""
import argparse
import hashlib
import json
import os
import tempfile
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from apps.triage.export import build_record


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def money(value):
    result = Decimal(str(value))
    if not result.is_finite() or result < 0:
        raise ValueError('Invalid nonnegative amount')
    return result


def atomic_export(path, records):
    descriptor, name = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(descriptor, 'w') as stream:
            json.dump(records, stream, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def accounted(events, config):
    """Completed usage replaces maxima only with complete, bounded counters."""
    reservations = {e['request_id']: e for e in events if e['state'] == 'reserved'}
    completed = {e['request_id'] for e in events if e['state'] == 'completed'}
    returned = {e['request_id']: e for e in events if e['state'] == 'provider_returned'}
    total = Decimal(0)
    settlements = []
    for request_id, reservation in reservations.items():
        amount = money(reservation['reservation'])
        response = returned.get(request_id, {})
        usage = response.get('usage') or {}
        if (request_id in completed and response.get('model') == config['model']
                and all(type(usage.get(k)) is int and usage[k] >= 0
                        for k in ('input_tokens', 'output_tokens'))
                and usage['input_tokens'] <= config['input_token_bound']
                and usage['output_tokens'] <= config['output_token_cap']):
            estimate = (money(config['input_price_per_million']) * usage['input_tokens'] +
                        money(config['output_price_per_million']) * usage['output_tokens']) / Decimal(1000000)
            # Never increase budget by an inconsistent above-reservation estimate.
            amount = max(amount, estimate) if estimate > amount else estimate
            settlements.append({'state': 'reconciled', 'request_id': request_id,
                'accounted_estimate': str(amount), 'usage': usage,
                'pricing_source': config['official_price_source'],
                'actual_billed_cost': None})
        total += amount
    return total, settlements


class Runner:
    def __init__(self, directory, config, *, terminal_provider_failures=False):
        self.directory = Path(directory).resolve()
        if self.directory == Path('/tmp') or Path('/tmp') in self.directory.parents:
            raise ValueError('Select persistent project runtime storage')
        self.directory.mkdir(parents=True, exist_ok=True)
        self.terminal_provider_failures = terminal_provider_failures
        self.config = config
        self.path = self.directory / 'events.jsonl'

    def append(self, event):
        with self.path.open('a') as stream:
            stream.write(json.dumps(event) + '\n')
            stream.flush()
            os.fsync(stream.fileno())
        fd = os.open(self.directory, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    def run(self, cases, provider=None, *, execute=False):
        # Exclusive process lock prevents simultaneous budget reservations.
        import fcntl
        with (self.directory / 'lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            return self._run(cases, provider, execute)

    def _run(self, cases, provider, execute):
        if not cases or len({c['sample_id'] for c in cases}) != len(cases) or (not self.config.get('benchmark') and len(cases) != 5):
            raise ValueError('Exactly five distinct samples required')
        config_hash = digest(self.config)
        events = [json.loads(line) for line in self.path.read_text().splitlines()] if self.path.exists() else []
        if any(e.get('config_hash', config_hash) != config_hash for e in events):
            raise ValueError('Immutable runner configuration mismatch')
        inference = provider.inference_identity() if hasattr(provider, 'inference_identity') else None
        if execute and not self.config.get('benchmark') and any(e.get('inference') != inference for e in events if e['state'] == 'reserved'):
            raise ValueError('Prompt/schema mismatch; use a new run directory after reconciliation')
        started = {e['request_id']: e for e in events if e['state'] == 'reserved'}
        finished = {e['request_id']: e for e in events if e['state'] == 'completed'}
        if execute and self.terminal_provider_failures:
            failed = {e['request_id']: e for e in events if e['state'] == 'failed'}
            raw = {e.get('request_id') for e in events if e['state'] == 'raw_response'}
            for rid in started.keys() - finished.keys():
                if rid in failed and rid in raw:
                    reservation = started[rid]
                    matches = [c for c in cases if c['sample_id'] == reservation['sample_id']]
                    if len(matches) != 1:
                        continue
                    case = matches[0]
                    event = self.failure_record(rid, reservation['identity'], case, failed[rid])
                    self.append(event)
                    finished[rid] = event
        if started.keys() - finished.keys():
            raise ValueError('Unresolved attempt: reservation retained; reconcile before spending')
        complete = {e['identity']: e['result'] for e in finished.values() if e['state'] == 'completed'}
        identities = [digest([c, config_hash, inference]) for c in cases]
        if not execute:
            return {'dry_run': True, 'pending': sum(i not in complete for i in identities)}
        cfg = self.config
        history = cfg.get('reconciled_history')
        if not history or not history.get('evidence'):
            raise ValueError('Historical five calls unresolved')
        if provider is None or not getattr(provider, 'enforces_bounds', False):
            raise ValueError('Bound-enforcing provider required')
        if not cfg.get('official_price_source') or not cfg.get('model'):
            raise ValueError('Documented official model prices required')
        for key in ('input_token_bound', 'output_token_cap'):
            if type(cfg.get(key)) is not int or cfg[key] <= 0:
                raise ValueError('Positive token bounds required')
        reserve = (money(cfg['input_price_per_million']) * cfg['input_token_bound'] +
                   money(cfg['output_price_per_million']) * cfg['output_token_cap']) / Decimal(1000000)
        spent = money(history['known_cost']) + money(history['unknown_reservation'])
        accounted_total, settlements = accounted(events, cfg)
        reconciled = {e['request_id'] for e in events if e['state'] == 'reconciled'}
        for settlement in settlements:
            if settlement['request_id'] not in reconciled:
                self.append(settlement)
        spent += accounted_total
        budget = money(cfg['budget'])
        if spent + reserve > budget and any(i not in complete for i in identities):
            raise ValueError('Budget preflight rejected')
        if hasattr(provider, 'preflight'):
            provider.preflight([c['message'] for c in cases], cfg)
        for case, identity in zip(cases, identities, strict=True):
            if identity in complete:
                continue
            if spent + reserve > budget:
                raise ValueError('Budget preflight rejected')
            request_id = str(uuid.uuid4())
            received_at = datetime.now(UTC).isoformat()
            self.append({'state': 'reserved', 'request_id': request_id, 'identity': identity,
                             'sample_id': case['sample_id'], 'config_hash': config_hash, 'inference': inference,
                             'model': cfg['model'], 'cap': cfg['output_token_cap'],
                             'input_fingerprint': digest(case['message']), 'reservation': str(reserve)})
            try:
                # Associate raw evidence with the reservation before provider validation.
                underlying = getattr(provider, 'provider', None)
                if underlying is not None:
                    underlying.raw_sink = lambda payload, request_id=request_id, identity=identity, case=case: self.append({
                        'state': 'raw_response', 'request_id': request_id,
                        'identity': identity, 'sample_id': case['sample_id'],
                        'payload': payload})
                result = provider(case['message'], cfg)
                self.append({'state': 'provider_returned', 'request_id': request_id,
                             'usage': result.usage, 'model': result.model})
                completed_at = datetime.now(UTC).isoformat()
                payload = build_record(
                    request={'id': request_id, 'source': case['source'],
                             'message': case['message'], 'received_at': received_at},
                    analysis=result.analysis, output=result, completed_at=completed_at,
                    attempt_id=request_id, attempts=[{'id': request_id, 'error': None,
                        'latency_ms': result.latency_ms, 'usage': result.usage}])
                self.append({'state': 'completed', 'request_id': request_id, 'identity': identity, 'result': payload})
                complete[identity] = payload
                current = [json.loads(line) for line in self.path.read_text().splitlines()]
                total, settlements = accounted(current, cfg)
                existing = {e['request_id'] for e in current if e['state'] == 'reconciled'}
                for settlement in settlements:
                    if settlement['request_id'] not in existing:
                        self.append(settlement)
                spent = money(history['known_cost']) + money(history['unknown_reservation']) + total
            except Exception as exc:
                self.append({'state': 'failed', 'request_id': request_id, 'identity': identity, 'error': 'provider_or_validation_failure',
                             'usage': getattr(exc, 'usage', None)})
                from apps.triage.providers.openai_provider import ProviderError
                if not self.terminal_provider_failures or not isinstance(exc, ProviderError):
                    raise
                event = self.failure_record(request_id, identity, case, {
                    'usage': getattr(exc, 'usage', None), 'latency_ms': getattr(exc, 'latency_ms', None)})
                self.append(event)
                complete[identity] = event['result']
                spent += reserve
        records = [complete[i] for i in identities]
        atomic_export(self.directory / 'assessment_outputs.json', records)
        return records


    @staticmethod
    def failure_record(request_id, identity, case, failure):
        return {'state': 'completed', 'request_id': request_id, 'identity': identity,
            'result': {'request': {'id': request_id, 'source': case['source'], 'message': case['message']},
                'analysis': None, 'decision': None, 'error': 'provider_or_validation_failure',
                'processing': {'unknown_cost': True, 'estimated_cost': None,
                    'attempts': [{'id': request_id, 'usage': failure.get('usage'),
                                  'latency_ms': failure.get('latency_ms')}]}}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime-dir', required=True)
    args = parser.parse_args()
    from apps.intake.sample_data import samples
    print(json.dumps(Runner(args.runtime_dir, {}).run(samples())))


if __name__ == '__main__':
    main()
