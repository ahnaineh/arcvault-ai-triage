"""Durable, offline-first acceptance journal. No credential discovery or live adapter."""
import argparse
import hashlib
import json
import os
import tempfile
import uuid
from dataclasses import asdict
from decimal import Decimal
from pathlib import Path

from apps.triage.schemas import validate_analysis


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


class Runner:
    def __init__(self, directory, config):
        self.directory = Path(directory).resolve()
        if self.directory == Path('/tmp') or Path('/tmp') in self.directory.parents:
            raise ValueError('Select persistent project runtime storage')
        self.directory.mkdir(parents=True, exist_ok=True)
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
        if len(cases) != 5 or len({c['sample_id'] for c in cases}) != 5:
            raise ValueError('Exactly five distinct samples required')
        config_hash = digest(self.config)
        events = [json.loads(line) for line in self.path.read_text().splitlines()] if self.path.exists() else []
        started = {e['request_id']: e for e in events if e['state'] == 'reserved'}
        finished = {e['request_id']: e for e in events if e['state'] in ('completed', 'failed')}
        if started.keys() - finished.keys():
            raise ValueError('Unresolved attempt: reservation retained; reconcile before spending')
        complete = {e['identity']: e['result'] for e in finished.values() if e['state'] == 'completed'}
        identities = [digest([c, config_hash]) for c in cases]
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
        spent += sum((money(e['reservation']) for e in started.values()), Decimal(0))
        budget = money(cfg['budget'])
        if spent + reserve * sum(i not in complete for i in identities) > budget:
            raise ValueError('Budget preflight rejected')
        for case, identity in zip(cases, identities, strict=True):
            if identity in complete:
                continue
            request_id = str(uuid.uuid4())
            self.append({'state': 'reserved', 'request_id': request_id, 'identity': identity,
                             'sample_id': case['sample_id'], 'config_hash': config_hash,
                             'model': cfg['model'], 'cap': cfg['output_token_cap'],
                             'input_fingerprint': digest(case['message']), 'reservation': str(reserve)})
            try:
                result = provider(case['message'], cfg)
                validate_analysis(result.analysis.model_dump(), case['message'])
                payload = asdict(result)
                payload['analysis'] = result.analysis.model_dump()
                self.append({'state': 'completed', 'request_id': request_id, 'identity': identity, 'result': payload})
                complete[identity] = payload
            except Exception:
                self.append({'state': 'failed', 'request_id': request_id, 'identity': identity, 'error': 'provider_or_validation_failure'})
                raise
        records = [complete[i] for i in identities]
        atomic_export(self.directory / 'assessment_outputs.json', records)
        return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime-dir', required=True)
    args = parser.parse_args()
    from apps.intake.sample_data import samples
    print(json.dumps(Runner(args.runtime_dir, {}).run(samples())))


if __name__ == '__main__':
    main()
