import copy
import unittest
from evals.score import load,validate,score
class EvaluationTests(unittest.TestCase):
 def test_dataset(self): self.assertTrue(validate(load()))
 def test_family_leakage(self):
  cases=load(); cases[-1]['scenario_family']=cases[5]['scenario_family']
  with self.assertRaises(AssertionError): validate(cases)
 def prediction(self):
  return dict(id='assessment-01',analysis=dict(category='Bug Report',priority='High',confidence=.9,core_issue='Login fails.',entities=[dict(type='url',value='arcvault.io/user/jsmith',evidence='arcvault.io/user/jsmith'),dict(type='error_code',value='403',evidence='403'),dict(type='time_expression',value='this morning',evidence='this morning'),dict(type='time_expression',value='last Tuesday',evidence='last Tuesday')],urgency=dict(level='High',evidence=[]),signals={k:dict(value=False,evidence=[]) for k in ['active_service_outage','insufficient_information','conflicting_intents']},billing_comparison=None,summary_sentences=['The customer reports a 403 while signing in this morning.','The affected account is arcvault.io/user/jsmith; the problem began after last Tuesday’s update.']),decision=dict(standard_destination='Engineering',final_destination='Engineering',human_escalation=False,escalation_reasons=[]))
 def test_paraphrase_requires_review(self):
  p=self.prediction(); c=load()[:1]
  self.assertEqual(score(c,[p])['rows'][0]['manual_summary_review'],'review_needed')
  p['summary_review']=dict(reviewer='independent-test-reviewer',all_required_facts=True,no_unsupported_claims=True)
  self.assertEqual(score(c,[p])['metrics']['end_to_end_success']['count'],1)
 def test_hallucination_and_omission(self):
  for text in ['Login failed.','The database was corrupted and engineers repaired it.']:
   p=self.prediction(); p['analysis']['summary_sentences']=[text,'The customer needs help.']
   p['summary_review']=dict(reviewer='reviewer',all_required_facts=False,no_unsupported_claims=False)
   self.assertFalse(score(load()[:1],[p])['rows'][0]['summary_constraints'])
 def test_entities(self):
  for entities in [[],[dict(type='other',value='invented',evidence='invented')]]:
   p=self.prediction(); p['analysis']['entities']=entities
   self.assertFalse(score(load()[:1],[p])['rows'][0]['entities'])
 def test_failures(self):
  c=load()[:1]
  self.assertEqual(score(c,[])['metrics']['missing']['count'],1)
  r=score(c,[dict(id=c[0]['id'],analysis={'bad':True},error='refusal')])
  self.assertEqual(r['metrics']['invalid_analysis']['count'],1)
  self.assertEqual(r['metrics']['operational_failures']['count'],1)
  self.assertEqual(r['metrics']['end_to_end_success']['count'],0)
 def test_duplicate(self):
  p=self.prediction()
  with self.assertRaises(ValueError): score(load()[:1],[p,p])
