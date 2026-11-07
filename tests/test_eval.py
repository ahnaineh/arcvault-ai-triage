import unittest

from evals.score import load, score, validate


class EvaluationTests(unittest.TestCase):
 def test_dataset(self): self.assertTrue(validate(load()))
 def test_family_leakage(self):
  cases=load(); cases[-1]['scenario_family']=cases[5]['scenario_family']
  with self.assertRaises(AssertionError): validate(cases)
 def prediction(self):
  return {'id': 'assessment-01','analysis': {'category': 'Bug Report','priority': 'High','confidence': .9,'core_issue': 'Login fails.','entities': [{'type': 'url','value': 'arcvault.io/user/jsmith','evidence': 'arcvault.io/user/jsmith'},{'type': 'error_code','value': '403','evidence': '403'},{'type': 'time_expression','value': 'this morning','evidence': 'this morning'},{'type': 'time_expression','value': 'last Tuesday','evidence': 'last Tuesday'}],'urgency': {'level': 'High','evidence': []},'signals': {k:{'value': False,'evidence': []} for k in ['active_service_outage','insufficient_information','conflicting_intents']},'billing_comparison': None,'summary_sentences': ['The customer reports a 403 while signing in this morning.','The affected account is arcvault.io/user/jsmith; the problem began after last Tuesday’s update.']},'decision': {'standard_destination': 'Engineering','final_destination': 'Engineering','human_escalation': False,'escalation_reasons': []}}
 def test_paraphrase_requires_review(self):
  p=self.prediction(); c=load()[:1]
  self.assertEqual(score(c,[p])['rows'][0]['manual_summary_review'],'review_needed')
  p['summary_review']={'reviewer': 'independent-test-reviewer','all_required_facts': True,'no_unsupported_claims': True}
  self.assertEqual(score(c,[p])['metrics']['end_to_end_success']['count'],1)
 def test_hallucination_and_omission(self):
  for text in ['Login failed.','The database was corrupted and engineers repaired it.']:
   p=self.prediction(); p['analysis']['summary_sentences']=[text,'The customer needs help.']
   p['summary_review']={'reviewer': 'reviewer','all_required_facts': False,'no_unsupported_claims': False}
   self.assertFalse(score(load()[:1],[p])['rows'][0]['summary_constraints'])
 def test_entities(self):
  for entities in [[],[{'type': 'other','value': 'invented','evidence': 'invented'}]]:
   p=self.prediction(); p['analysis']['entities']=entities
   self.assertFalse(score(load()[:1],[p])['rows'][0]['entities'])
 def test_failures(self):
  c=load()[:1]
  self.assertEqual(score(c,[])['metrics']['missing']['count'],1)
  r=score(c,[{'id': c[0]['id'],'analysis': {'bad':True},'error': 'refusal'}])
  self.assertEqual(r['metrics']['invalid_analysis']['count'],1)
  self.assertEqual(r['metrics']['operational_failures']['count'],1)
  self.assertEqual(r['metrics']['end_to_end_success']['count'],0)
 def test_duplicate(self):
  p=self.prediction()
  with self.assertRaises(ValueError): score(load()[:1],[p,p])
 def test_review_denominators(self):
  cases=load()[:2]
  cases[0]['expected_policy']['human_escalation']=True
  cases[1]['expected_policy']['human_escalation']=True
  p=self.prediction()
  self.assertEqual(score(cases,[p])['conditional_routing']['missed_escalations'],{'count': 1,'denominator': 2})
  cases[0]['expected_policy']['human_escalation']=False
  p['analysis']={}
  p['decision']['human_escalation']=True
  self.assertEqual(score(cases,[p])['conditional_routing']['unnecessary_escalations'],{'count': 0,'denominator': 0})
 def test_malformed_fields(self):
  for field,value in [('summary_sentences',None),('summary_sentences',[1,2]),('entities',[None]),('signals',True)]:
   p=self.prediction(); p['analysis'][field]=value
   self.assertEqual(score(load()[:1],[p])['metrics']['invalid_analysis']['count'],1)
 def test_assessment_onset(self):
  self.assertIn({'type': 'time_expression','value': '2pm EST','evidence': '2pm EST'},load()[4]['required_entities'])

 def test_unhashable_entities_continue_report(self):
  import copy
  for field in ['type','value']:
   for value in [[], {}]:
    bad=self.prediction(); bad['analysis']['entities'][0][field]=value
    good=self.prediction(); good['id']='good'
    cases=copy.deepcopy(load()[:1])*2
    cases[1]=copy.deepcopy(cases[1]); cases[1]['id']='good'
    report=score(cases,[bad,good])
    self.assertEqual(len(report['rows']),2)
    self.assertFalse(report['rows'][0]['schema'])
    self.assertFalse(report['rows'][0]['entities'])
    self.assertTrue(report['rows'][1]['schema'])
    self.assertTrue(report['rows'][1]['entities'])
