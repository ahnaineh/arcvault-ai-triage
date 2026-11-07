import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_review_coverage_and_human_gate():
    data = json.loads((ROOT / 'evals/dataset.json').read_text())
    sheet = json.loads((ROOT / 'docs/evidence/review-followups/summary-review-sheet.json').read_text())
    assert {r['id'] for r in sheet} == {r['id'] for r in data}
    assert all(r['human_accept'] is None and r['reviewer_kind'] == 'ASSISTANT' for r in sheet)
    assert sum(r['assistant_verdict'] == 'correction_requested' for r in sheet) == 2


def test_fresh_inputs_are_disjoint_and_frozen():
    old = json.loads((ROOT / 'evals/dataset.json').read_text())
    new = json.loads((ROOT / 'evals/fresh_holdout.json').read_text())
    assert len({r['id'] for r in new}) == len(new) == 8
    assert len({r['message'] for r in new}) == len(new)
    assert not {r['message'].casefold() for r in new} & {r['message'].casefold() for r in old}
    assert all(r['split'] == 'fresh_holdout' and r['summary_required_facts'] and r['expected_final_destination'] for r in new)
