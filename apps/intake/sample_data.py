import json
from pathlib import Path


def samples():
    return json.loads((Path(__file__).resolve().parents[2] / 'samples/inputs.json').read_text())


def sample_key(item):
    return f'assessment-v1:{item["sample_id"]}'
