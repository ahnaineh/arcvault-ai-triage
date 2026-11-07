"""Convert canonical application exports; never infer manual summary acceptance."""
import argparse
import json
from pathlib import Path


def adapt(records, cases):
    predictions = []
    for record in records:
        request = record.get('request') or {}
        matches = [c for c in cases if c['message'] == request.get('message')
                   and c['source'] == request.get('source')]
        if len(matches) != 1:
            raise ValueError('export request must match exactly one case by source and message')
        decision = record.get('decision')
        prediction = {'id': matches[0]['id'], 'analysis': record.get('analysis'),
                      'decision': {k: decision[k] for k in (
                          'standard_destination', 'final_destination',
                          'human_escalation', 'escalation_reasons') if k in decision}
                      if isinstance(decision, dict) else decision,
                      'provenance': record.get('provenance'),
                      'processing': record.get('processing'),
                      'application_review': record.get('review')}
        processing = record.get('processing') or {}
        attempts = processing.get('attempts') or []
        latencies = [attempt.get('latency_ms') for attempt in attempts]
        prediction['latency_ms'] = (sum(latencies) if latencies and
            all(isinstance(value, (int, float)) and not isinstance(value, bool)
                for value in latencies) else None)
        prediction['cost_usd'] = (processing.get('estimated_cost')
            if processing.get('unknown_cost') is False else None)
        if record.get('error') or not isinstance(record.get('analysis'), dict):
            prediction['error'] = record.get('error') or 'missing_or_malformed_output'
        predictions.append(prediction)
    return predictions


def main():
    from evals.score import load
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('exports')
    parser.add_argument('predictions')
    args = parser.parse_args()
    Path(args.predictions).write_text(json.dumps(
        adapt(json.loads(Path(args.exports).read_text()), load()), indent=2) + '\n')


if __name__ == '__main__':
    main()
