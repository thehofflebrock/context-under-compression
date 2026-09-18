import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('runner',ROOT/'python/runner.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)

def fixture():
    run=json.loads((ROOT/'dist/demo.json').read_text())
    run['demo']=False
    run['brief']['sourceText']='Captured source with qualifications.'
    run['records']={s:[] for s in r.STAGES}
    run['decisions']=[]
    return run

class PipelineTests(unittest.TestCase):
    def test_all_stages_use_fresh_calls_and_carry_brief(self):
        run=fixture();calls=[]
        def mock(prompt,model,key):
            calls.append(prompt)
            return 'Response with a qualification.',{'model':'mock','usage':{'input_tokens':1}}
        for stage in r.STAGES:r.execute_stage(run,stage,'mock','not-a-key',mock)
        self.assertEqual(len(calls),4)
        for prompt in calls:
            self.assertIn('"minWords": 200',prompt)
            self.assertIn('Captured source',prompt)
        self.assertIn('Response with a qualification.',calls[-1])
        self.assertEqual(len(run['records']['revision']),1)
    def test_retrieval_and_dependency_guards(self):
        run=fixture();run['brief']['sourceText']=''
        with self.assertRaisesRegex(ValueError,'Captured source'):r.prompt_for(run,'draft')
        run=fixture()
        with self.assertRaisesRegex(ValueError,'prerequisite'):r.prompt_for(run,'review')
    def test_checkpoint_survives_later_error(self):
        run=fixture()
        r.execute_stage(run,'draft','mock','',lambda *_:('Draft',{'model':'mock'}))
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'checkpoint.json';r.save_atomic(p,run)
            def fail(*_):raise RuntimeError('Unavailable')
            with self.assertRaises(RuntimeError):r.execute_stage(run,'review','mock','',fail)
            self.assertEqual(len(json.loads(p.read_text())['records']['draft']),1)
            self.assertEqual(run['records']['review'],[])
    def test_truncated_provider_result_not_saved(self):
        class Response:
            def __enter__(self):return self
            def __exit__(self,*a):pass
            def read(self):return json.dumps({'stop_reason':'max_tokens','content':[{'type':'text','text':'Partial'}]}).encode()
        with patch.object(r.urllib.request,'urlopen',return_value=Response()):
            with self.assertRaisesRegex(RuntimeError,'truncated'):r.call_api('test','test','fake')
    def test_new_decisions_mark_revision_stale(self):
        run=fixture()
        for s in r.STAGES:r.execute_stage(run,s,'mock','',lambda *_:('Response',{'model':'mock'}))
        run['decisions'].append({'id':'new','claim':'Scope','verdict':'accept','reason':'Evidence'})
        self.assertTrue(r.stale(run,'revision'))

if __name__=='__main__':unittest.main()
