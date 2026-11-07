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
        a = a if isinstance(a, dict) else {}
        d = d if isinstance(d, dict) else {}
        valid=matches(a,schema)
        expected_entities={(e['type'],e['value'],e['evidence']) for e in c['required_entities']}
        actual_entities={(e.get('type'),e.get('value'),e.get('evidence')) for e in a.get('entities',[]) if isinstance(e,dict)} if isinstance(a.get('entities',[]),list) else set()
        review=p.get('summary_review', {})
        reviewed=bool(review.get('reviewer')) and review.get('all_required_facts') is True and review.get('no_unsupported_claims') is True
        row=dict(id=c['id'], category=a.get('category') in c['acceptable_categories'], priority=a.get('priority') in c['acceptable_priorities'], entities=valid and actual_entities==expected_entities, signals=valid and all(a.get('signals',{}).get(k,{}).get('value','missing')==v for k,v in c['expected_signals'].items()), schema=valid, summary_constraints=valid and reviewed, routing=valid and d==c['expected_policy'], manual_summary_review='accepted' if reviewed else 'review_needed', missing=not bool(p), invalid_analysis=bool(p) and not valid)

        automatic=bool(p) and valid and d.get('human_escalation') is False
        expected=c['expected_policy']['human_escalation']
        row.update(automatic=automatic, missed_escalations=automatic and expected, unnecessary_escalations=d.get('human_escalation') is True and not expected, incorrect_automatic_routing=automatic and d.get('final_destination')!=c['expected_policy']['final_destination'])
        for k in totals: totals[k]+=int(row[k])
        rows.append(row)
    totals.update(missing=sum(r['missing'] for r in rows), invalid_analysis=sum(r['invalid_analysis'] for r in rows), operational_failures=sum(bool(p.get('error')) for p in predictions), completed=sum(r['schema'] for r in rows), end_to_end_success=sum(all(r[k] for k in ['schema','category','priority','entities','signals','summary_constraints','routing']) for r in rows))
    conditional = dict(missed_escalations=dict(count=totals['missed_escalations'], denominator=sum(r['automatic'] and c['expected_policy']['human_escalation'] for r,c in zip(rows,cases))), unnecessary_escalations=dict(count=totals['unnecessary_escalations'],denominator=sum(r['schema'] and by_id.get(c['id'],{}).get('decision',{}).get('human_escalation') is True for r,c in zip(rows,cases))), incorrect_automatic_routing=dict(count=totals['incorrect_automatic_routing'],denominator=totals['automatic']))
    return dict(conditional_routing=conditional,cases=len(cases),predictions=len(predictions),metrics={k:dict(count=v,denominator=len(cases)) for k,v in totals.items()},coverage=dict(count=len(predictions),denominator=len(cases)),cost_inputs=[p.get('cost_usd') for p in predictions],latency_inputs_ms=[p.get('latency_ms') for p in predictions],rows=rows)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['validate','score']); parser.add_argument('predictions',nargs='?'); parser.add_argument('--split',choices=['assessment','development','validation','test'],default='development'); parser.add_argument('--unlock-test',action='store_true')
    args=parser.parse_args(); cases=load(); validate(cases)
    if args.command=='validate': print('50 draft cases validated'); return
    if args.split=='test' and not args.unlock_test: parser.error('locked test requires --unlock-test after configuration freeze')
    print(json.dumps(score([c for c in cases if c['split']==args.split],json.loads(Path(args.predictions).read_text())),indent=2))
if __name__=='__main__': main()
