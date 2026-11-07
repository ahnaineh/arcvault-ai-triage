import json,math,shutil
from decimal import Decimal
from pathlib import Path
from apps.triage.acceptance import accounted
from apps.triage.schemas import validate_analysis
from evals.score import matches
src=Path('.acceptance-runtime/comparison-v3'); dst=Path('docs/evidence/comparison-v3')
for p in src.glob('*.json'):shutil.copyfile(p,dst/p.name)
reports={}; scores={}
cases={c['id']:c for c in json.loads(Path('evals/dataset.json').read_text())}
schema=json.loads(Path('contracts/analysis.schema.json').read_text())
for model,prices in [('gpt-6-luna',('.1','.5')),('gpt-6.1-terra',('1','5'))]:
 d=src/model;target=dst/model;target.mkdir(exist_ok=True)
 for p in d.glob('*.json*'):shutil.copyfile(p,target/p.name)
 e=[json.loads(x) for x in (d/'events.jsonl').read_text().splitlines()];config=json.loads((d/'config.json').read_text());r={x['request_id']:x for x in e if x['state']=='reserved'}
 raw={x['request_id']:x['payload'] for x in e if x['state']=='raw_response'}; completed={x['request_id']:x['result'] for x in e if x['state']=='completed'}
 lat=[a['latency_ms'] for x in completed.values() for a in x['processing']['attempts'] if isinstance(a.get('latency_ms'),(int,float))];lat.sort()
 usages=[x.get('usage') or {} for x in raw.values()];i=sum(x.get('input_tokens',0) for x in usages);o=sum(x.get('output_tokens',0) for x in usages)
 cost=(Decimal(prices[0])*i+Decimal(prices[1])*o)/1000000
 scores[model]=json.loads((d/'score.json').read_text())
 reports[model]={'calls':len(r),'input_tokens':i,'output_tokens_including_reasoning':o,'reasoning_tokens':sum(x.get('reasoning_tokens',0) for x in usages),'standard_price_estimate_usd':str(cost),'conservative_accounted_usd':str(accounted(e,config)[0]),'latency_count':len(lat),'latency_p50_ms':lat[math.ceil(.5*len(lat))-1],'latency_p95_ms':lat[math.ceil(.95*len(lat))-1],'failures':sum(x['state']=='failed' for x in e),'incomplete_responses':sum(x.get('status')=='incomplete' for x in raw.values()),'metrics':scores[model]['metrics'],'conditional_routing':scores[model]['conditional_routing'],'per_case':[], 'raw_structural_schema_pass':0, 'rejection_details':[]}
 for rid,res in r.items():
  try:
   analysis=json.loads(raw[rid]['output_text'][0])
   reports[model]['raw_structural_schema_pass'] += int(matches(analysis,schema))
   validate_analysis(analysis,cases[res['sample_id']]['message'])
  except Exception as exc:
   reports[model]['rejection_details'].append({'id':res['sample_id'],'reason':str(exc).split(' [type=')[0]})
  reports[model]['per_case'].append({'id':res['sample_id'],'usage':raw.get(rid,{}).get('usage'),'status':raw.get(rid,{}).get('status'),'error':completed.get(rid,{}).get('error'),'latency_ms':completed.get(rid,{}).get('processing',{}).get('attempts',[{}])[0].get('latency_ms')})
a={r['id']:r for r in scores['gpt-6-luna']['rows']};b={r['id']:r for r in scores['gpt-6.1-terra']['rows']}
paired={}
for k in ['category','priority','entities','signals','schema','routing']:
 wins=[i for i in a if a[i][k] and not b[i][k]];losses=[i for i in a if b[i][k] and not a[i][k]]
 paired[k]={'luna_wins':wins,'terra_wins':losses,'both_pass':sum(a[i][k] and b[i][k] for i in a),'both_fail':sum(not a[i][k] and not b[i][k] for i in a)}
total=Decimal('19.01065694')+sum(Decimal(x['conservative_accounted_usd']) for x in reports.values())
output={'set_status':'reused comparison set, not fresh holdout','models':reports,'paired':paired,'total_project_accounted_usd':str(total),'project_ceiling_usd':'83','actual_billed_cost':None}
(dst/'results.json').write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps({m:{k:v for k,v in x.items() if k not in ['metrics','per_case','conditional_routing']} for m,x in reports.items()},indent=2));print('total',total)
for m,x in reports.items():print(m,{k:v['count'] for k,v in x['metrics'].items()})
print('paired',json.dumps(paired))
