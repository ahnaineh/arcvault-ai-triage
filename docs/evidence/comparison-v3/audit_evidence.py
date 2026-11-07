import json
from pathlib import Path

root=Path('docs/evidence/comparison-v3');cases={c['id']:c for c in json.loads(Path('evals/dataset.json').read_text())};events=[json.loads(x) for x in (root/'gpt-6-luna/events.jsonl').read_text().splitlines()];reserved={e['request_id']:e for e in events if e['state']=='reserved'};failed={e['request_id'] for e in events if e['state']=='failed'};rows=[]
def excerpts(v,path=''):
 if isinstance(v,dict):
  for k,x in v.items():
   if k=='evidence':
    if isinstance(x,str):yield f'{path}.evidence',x
    else:
     for i,s in enumerate(x):yield f'{path}.evidence[{i}]',s
   else:yield from excerpts(x,f'{path}.{k}')
 elif isinstance(v,list):
  for i,x in enumerate(v):yield from excerpts(x,f'{path}[{i}]')
for e in events:
 if e['state']=='raw_response' and e['request_id'] in failed:
  cid=reserved[e['request_id']]['sample_id'];p=e['payload'];a=json.loads(p['output_text'][0]);bad=[{'path':k.lstrip('.'),'returned_excerpt':v,'exact_substring':False,'matches_after_removing_outer_curly_quotes':v.strip('“”') in cases[cid]['message']} for k,v in excerpts(a) if v not in cases[cid]['message']];rows.append({'case_id':cid,'request_id':e['request_id'],'provider_response_id':p['id'],'provider_status':p['status'],'source_message':cases[cid]['message'],'invalid_excerpts':bad})
(root/'luna-evidence-failures.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False)+'\n');print('failed cases',len(rows),'bad excerpts',sum(len(r['invalid_excerpts']) for r in rows));print('quote-only',sum(x['matches_after_removing_outer_curly_quotes'] for r in rows for x in r['invalid_excerpts']))
for r in rows:print(r['case_id'],r['invalid_excerpts'])
