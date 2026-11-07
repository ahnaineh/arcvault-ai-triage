import copy
import unittest
from evals.score import load, validate, score

class EvaluationTests(unittest.TestCase):
    def test_dataset(self):
        self.assertTrue(validate(load()))
    def test_family_leakage(self):
        cases=load(); cases[5]['scenario_family']=cases[0]['scenario_family']
        with self.assertRaises(AssertionError): validate(cases)
    def test_good_and_bad(self):
        c=load()[5]
        a=dict(category=c['acceptable_categories'][0],priority=c['acceptable_priorities'][0],confidence=.9,core_issue=c['message'],entities=[dict(**e,evidence=e['value']) for e in c['required_entities']],urgency=dict(level='High',evidence=[]),signals={k:dict(value=v,evidence=[]) for k,v in c['expected_signals'].items()},billing_comparison=None,summary_sentences=[c['message'],'The customer requests assistance.'])
        p=dict(id=c['id'],analysis=a,decision=c['expected_policy'])
        good=score([c],[p]); self.assertTrue(all(good['rows'][0][k] for k in ['category','priority','entities','signals','schema','summary_constraints','routing']))
        bad=copy.deepcopy(p); bad['analysis'].update(category='nonsense',priority='Low',entities=[],signals={},summary_sentences=['Guaranteed resolution tomorrow']); bad['decision']={}
        result=score([c],[bad]); self.assertTrue(all(not result['rows'][0][k] for k in ['category','priority','entities','signals','schema','summary_constraints','routing']))
        self.assertEqual(score([c],[])['coverage']['count'],0)
        with self.assertRaises(ValueError): score([c],[p,p])
    def test_missed_escalation(self):
        c=load()[9]; base=load()[5]
        # A schema-valid response can still route an outage incorrectly.
        a=dict(category='Bug Report',priority='High',confidence=.9,core_issue='Unavailable',entities=[],urgency=dict(level='High',evidence=[]),signals={k:dict(value=False,evidence=[]) for k in c['expected_signals']},billing_comparison=None,summary_sentences=['Unavailable.','Please investigate.'])
        r=score([c],[dict(id=c['id'],analysis=a,decision=dict(human_escalation=False,final_destination='Engineering'))])
        self.assertEqual(r['metrics']['missed_escalations']['count'],1)
