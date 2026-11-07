"""Run: python3 -m evals.score validate | score PREDICTIONS --split development."""
import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load():
    return json.loads((ROOT / 'evals/dataset.json').read_text())

def validate(cases):
    assert len(cases) == 50
    assert len({c['id'] for c in cases}) == 50
    families = {}
    for split, count in [('assessment', 5), ('development', 25), ('validation', 10), ('test', 10)]:
        assert sum(c['split'] == split for c in cases) == count
    for c in cases:
        assert families.setdefault(c['scenario_family'], c['split']) == c['split'], 'family leakage'
        for key in ('message','acceptable_categories','acceptable_priorities','expected_signals','expected_policy','summary_required_facts','summary_forbidden_facts','rationale','review_status'):
            assert c[key], key
        assert isinstance(c['required_entities'], list)
    return True

def matches(value, schema):
    if 'anyOf' in schema:
        return any(matches(value, s) for s in schema['anyOf'])
    types = schema.get('type', [])
    types = [types] if isinstance(types, str) else types
    actual = 'null' if value is None else 'boolean' if isinstance(value, bool) else 'number' if isinstance(value, (int,float)) else 'string' if isinstance(value,str) else 'array' if isinstance(value,list) else 'object' if isinstance(value,dict) else 'invalid'
    if actual not in types: return False
    if 'enum' in schema and value not in schema['enum']: return False
    if actual == 'number':
        return math.isfinite(value) and schema.get('minimum', -math.inf) <= value <= schema.get('maximum', math.inf)
    if actual == 'object':
        return all(k in value for k in schema.get('required', [])) and all(k in schema['properties'] and matches(v,schema['properties'][k]) for k,v in value.items())
    if actual == 'array':
        return schema.get('minItems',0) <= len(value) <= schema.get('maxItems',math.inf) and all(matches(v,schema['items']) for v in value)
    return True

def score(cases, predictions):
    ids = {c['id'] for c in cases}
    if len({p['id'] for p in predictions}) != len(predictions) or any(p['id'] not in ids for p in predictions):
        raise ValueError('duplicate or unknown prediction IDs')
    by_id = {p['id']:p for p in predictions}
    schema = json.loads((ROOT/'contracts/analysis.schema.json').read_text())
    totals = {k:0 for k in ['category','priority','entities','signals','schema','summary_constraints','routing','missed_escalations','unnecessary_escalations','incorrect_automatic_routing','automatic']}
    rows=[]
    for c in cases:
        p=by_id.get(c['id'], {}); a=p.get('analysis') or {}; d=p.get('decision') or {}
        summary=' '.join(a.get('summary_sentences', []))
        valid=matches(a,schema)
        row=dict(id=c['id'], category=a.get('category') in c['acceptable_categories'], priority=a.get('priority') in c['acceptable_priorities'], entities=all(any(e.get('type')==r['type'] and e.get('value')==r['value'] for e in a.get('entities',[])) for r in c['required_entities']), signals=all(a.get('signals',{}).get(k,{}).get('value','missing')==v for k,v in c['expected_signals'].items()), schema=valid, summary_constraints=all(f.casefold() in summary.casefold() for f in c['summary_required_facts']) and not any(f.casefold() in summary.casefold() for f in c['summary_forbidden_facts']), routing=d==c['expected_policy'], manual_summary_review='pending')
        automatic=bool(p) and valid and d.get('human_escalation') is False
        expected=c['expected_policy']['human_escalation']
        row.update(automatic=automatic, missed_escalations=automatic and expected, unnecessary_escalations=d.get('human_escalation') is True and not expected, incorrect_automatic_routing=automatic and d.get('final_destination')!=c['expected_policy']['final_destination'])
        for k in totals: totals[k]+=int(row[k])
        rows.append(row)
    return dict(cases=len(cases),predictions=len(predictions),metrics={k:dict(count=v,denominator=len(cases)) for k,v in totals.items()},coverage=dict(count=len(predictions),denominator=len(cases)),cost_inputs=[p.get('cost_usd') for p in predictions],latency_inputs_ms=[p.get('latency_ms') for p in predictions],rows=rows)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['validate','score']); parser.add_argument('predictions',nargs='?'); parser.add_argument('--split',choices=['assessment','development','validation','test'],default='development'); parser.add_argument('--unlock-test',action='store_true')
    args=parser.parse_args(); cases=load(); validate(cases)
    if args.command=='validate': print('50 draft cases validated'); return
    if args.split=='test' and not args.unlock_test: parser.error('locked test requires --unlock-test after configuration freeze')
    print(json.dumps(score([c for c in cases if c['split']==args.split],json.loads(Path(args.predictions).read_text())),indent=2))
if __name__=='__main__': main()
