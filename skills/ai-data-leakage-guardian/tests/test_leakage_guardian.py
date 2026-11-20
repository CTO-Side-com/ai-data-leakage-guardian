"""Synthetic offline behavior and failure-mode tests. No network dependencies."""
import base64
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import urllib.parse

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from guardian import initialize,validate,load,write,scan,plan,report,tasks,recheck,cell,catalog
from canary_audit import audit,detect,validate_manifest,MAX_FILE
spec=importlib.util.spec_from_file_location('adlg_demo',ROOT/'assets/demo_pipeline.py')
demo=importlib.util.module_from_spec(spec);spec.loader.exec_module(demo)

def evidence(result='contained_in_capture'):
    return {'id':'EV1','kind':'test','ref':'synthetic/observations.json','method':'Reviewed synthetic captured payloads',
        'reviewer':'Synthetic Reviewer','environment':'staging','scope':'Synthetic model request capture only',
        'observed_on':'2026-11-20','positive_control':'All seeded markers detected in positive control',
        'negative_case':'Restricted marker is not permitted at model sink','expected':'No restricted marker in complete captured payload',
        'observed':'Synthetic scoped capture observation','data_scope':'Known synthetic public and restricted fields',
        'sink_scope':'One explicitly instrumented synthetic model-request boundary','result':result}

class AssessmentTests(unittest.TestCase):
    def setUp(self):self.a=initialize('Synthetic AI application','staging')
    def bad(self):self.assertTrue(validate(self.a))
    def verified(self):
        self.a['evidence']=[evidence()];c=self.a['checks'][0]
        c.update(status='verified_in_scope',evidence_refs=['EV1'],reviewer='Synthetic Reviewer',rationale='Only synthetic model request capture was reviewed',verified_scope='One synthetic request payload under the two-marker fixture and supported representations')
        return c
    def test_initialization(self):self.assertEqual([],validate(self.a));self.assertEqual(37,len(self.a['checks']));self.assertTrue(all(c['status']=='insufficient_evidence' for c in self.a['checks']))
    def test_catalog_unique(self):self.assertEqual(37,len({c['id'] for c in catalog()['checks']}))
    def test_blank_product_rejected(self):
        with self.assertRaises(ValueError):initialize('','staging')
    def test_verified_capture(self):self.verified();self.assertEqual([],validate(self.a))
    def test_code_alone_not_runtime_verification(self):self.verified();self.a['evidence'][0]['kind']='code';self.bad()
    def test_leak_cannot_verify(self):self.verified();self.a['evidence'][0]['result']='leak_observed';self.bad()
    def test_inconclusive_cannot_verify(self):self.verified();self.a['evidence'][0]['result']='inconclusive';self.bad()
    def test_explicit_scope_required(self):self.verified()['verified_scope']='';self.bad()
    def test_test_data_scope_required(self):self.verified();self.a['evidence'][0]['data_scope']='';self.bad()
    def test_test_sink_scope_required(self):self.verified();self.a['evidence'][0]['sink_scope']='';self.bad()
    def test_positive_control_required(self):self.verified();self.a['evidence'][0]['positive_control']='';self.bad()
    def test_evidence_environment_matters(self):self.verified();self.a['evidence'][0]['environment']='production';self.bad()
    def test_future_evidence_rejected(self):self.verified();self.a['evidence'][0]['observed_on']='2099-01-01';self.bad()
    def test_unknown_reference_rejected(self):self.verified()['evidence_refs']=['missing'];self.bad()
    def test_duplicate_evidence_rejected(self):self.verified();self.a['evidence'].append(copy.deepcopy(self.a['evidence'][0]));self.bad()
    def test_missing_check_rejected(self):self.a['checks'].pop();self.bad()
    def test_malformed_status_rejected(self):self.a['checks'][0]['status']=[];self.bad()
    def test_malformed_kind_rejected(self):self.verified();self.a['evidence'][0]['kind']=[];self.bad()
    def test_malformed_watch_rejected(self):self.a['checks'][0]['watched_paths']=[None];self.bad()
    def test_unknown_catalog_rejected(self):self.a['catalog_version']='unknown';self.bad()
    def test_inapplicable_needs_human_approval(self):self.verified().update(status='not_applicable',approved_by='');self.bad()
    def test_confirmed_gap_needs_failure_or_code(self):
        c=self.verified();c.update(status='confirmed_gap',owner='Owner',severity='high',recommendation='Minimize before egress',verification_test='Repeat controlled capture');self.bad()
        self.a['evidence'][0]['result']='leak_observed';self.assertEqual([],validate(self.a))
    def test_sink_approval_needs_evidence(self):
        self.a['sinks']=[{'id':'model','kind':'provider','location_ref':'config/provider','purpose':'synthetic use','approval_status':'approved','approved_data_classes':['public'],'reviewer':'','approval_ref':'','retention_evidence_ref':'','training_evidence_ref':''}];self.bad()
    def test_flow_unknown_sink(self):
        self.a['data_flows']=[{'id':'FLOW1','source':'synthetic input','sink_id':'missing','purpose':'test','data_classes':['restricted'],'transformations':['redaction'],'evidence_ref':'src/redact.py'}];self.bad()
    def test_flow_and_sink_example_valid(self):self.assertEqual([],validate(load(ROOT/'assets/assessment-example.json')))
    def test_reports_and_tasks(self):
        with tempfile.TemporaryDirectory() as d:
            report(self.a,d,True);self.assertEqual(37,tasks(self.a,d));plan(self.a,Path(d,'plan.md'))
            self.assertTrue(Path(d,'AI-DATA-LEAKAGE.pdf').read_bytes().startswith(b'%PDF'))
            manifest=load(Path(d,'handoff-manifest.json'))
            for x in manifest['files']:self.assertEqual(x['sha256'],hashlib.sha256(Path(d,x['path']).read_bytes()).hexdigest())
    def test_report_preserves_data_flow_register(self):
        a=load(ROOT/'assets/assessment-example.json')
        with tempfile.TemporaryDirectory() as d:
            report(a,d);s=Path(d,'AI-DATA-LEAKAGE.md').read_text();self.assertIn('FLOW-MODEL',s);self.assertIn('Retention evidence: Unknown',s);self.assertIn('Training-use evidence: Unknown',s)
    def test_invalid_report_emits_no_files(self):
        self.a['checks'].pop()
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):report(self.a,d)
            self.assertEqual([],list(Path(d).iterdir()))
    def test_existing_plan_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d,'assessment.json');write(p,self.a);before=p.read_bytes()
            with self.assertRaises(FileExistsError):plan(self.a,p)
            self.assertEqual(before,p.read_bytes())
    def test_report_source_collision_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d,'assessment-redacted.json');write(p,self.a);before=p.read_bytes()
            r=subprocess.run([sys.executable,str(ROOT/'scripts/guardian.py'),'report','--assessment',str(p),'--out',d],capture_output=True,text=True)
            self.assertNotEqual(0,r.returncode);self.assertEqual(before,p.read_bytes())
    def test_symlink_report_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d,'sentinel');p.write_text('keep');Path(d,'AI-DATA-LEAKAGE.md').symlink_to(p)
            with self.assertRaises(ValueError):report(self.a,d)
            self.assertEqual('keep',p.read_text())
    def test_hardlink_report_source_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d,'assessment.json');write(p,self.a);before=p.read_bytes();os.link(p,Path(d,'AI-DATA-LEAKAGE.md'))
            r=subprocess.run([sys.executable,str(ROOT/'scripts/guardian.py'),'report','--assessment',str(p),'--out',d],capture_output=True,text=True)
            self.assertNotEqual(0,r.returncode);self.assertEqual(before,p.read_bytes())
    def test_hardlink_task_source_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d,'assessment.json');write(p,self.a);before=p.read_bytes();os.link(p,Path(d,'tasks-jira.csv'))
            r=subprocess.run([sys.executable,str(ROOT/'scripts/guardian.py'),'tasks','--assessment',str(p),'--out',d],capture_output=True,text=True)
            self.assertNotEqual(0,r.returncode);self.assertEqual(before,p.read_bytes())
    def test_exports_redacted_and_neutralized(self):
        self.a['product']='person@example.com';self.a['checks'][0]['recommendation']='@channel <https://bad.test> person@example.com'
        with tempfile.TemporaryDirectory() as d:
            report(self.a,d);tasks(self.a,d);s=Path(d,'tasks-slack.txt').read_text();self.assertNotIn('@channel',s);self.assertNotIn('person@example.com',s);self.assertNotIn('<https',s)
        self.assertTrue(cell('  =SUM(1,2)').startswith("'"))
    def test_recheck_preserves_baseline_and_invalidates_scope(self):
        self.verified();new=recheck(self.a,['src/model.py']);self.assertEqual('verified_in_scope',self.a['checks'][0]['status']);self.assertEqual('insufficient_evidence',new['checks'][0]['status']);self.assertEqual('',new['checks'][0]['verified_scope']);self.assertEqual(['EV1'],new['checks'][0]['stale_evidence'])
    def test_empty_recheck_preserves_assertions(self):self.verified();self.assertEqual([],recheck(self.a,[])['recheck']['invalidated'])
    def test_recheck_rejects_traversal(self):
        with self.assertRaises(ValueError):recheck(self.a,['../secret'])
    def test_scanner_metadata_only(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d,'app.py').write_text('logger.info(messages)\ninclude_raw=True\n');r=scan(d)
            self.assertEqual(2,len(r['findings']));self.assertNotIn('logger.info(messages)',json.dumps(r));self.assertTrue(all(x['status']=='unconfirmed_lead' for x in r['findings']))
    def test_scanner_skips_credentials_and_symlinks(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d,'credentials.json').write_text('logger.info(messages)');Path(d,'link.py').symlink_to(Path(d,'credentials.json'));self.assertEqual(0,scan(d)['files_considered'])
    def test_scanner_limits_visible(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d,'app.py').write_text('logger.info(messages)\nlogger.info(messages)');self.assertTrue(scan(d,max_findings=1)['limit_reached'])

class DetectorTests(unittest.TestCase):
    def setUp(self):self.m=load(ROOT/'assets/capture-manifest.json');self.markers=self.m['markers'];self.value=self.markers[1]['value']
    def found(self,payload):return {m['marker_id'] for m in detect(payload,self.markers)['matches']}
    def test_literal(self):self.assertIn('RESTRICTED',self.found(self.value.encode()))
    def test_base64_whole_json(self):self.assertIn('RESTRICTED',self.found(base64.b64encode(json.dumps({'document':self.value}).encode())))
    def test_base64_field_after_equals(self):self.assertIn('RESTRICTED',self.found(b'payload='+base64.b64encode(self.value.encode())))
    def test_base64url_without_padding(self):self.assertIn('RESTRICTED',self.found(base64.urlsafe_b64encode(self.value.encode()).rstrip(b'=')))
    def test_two_base64_layers(self):self.assertIn('RESTRICTED',self.found(base64.b64encode(base64.b64encode(self.value.encode()))))
    def test_mime_wrapped_base64(self):self.assertIn('RESTRICTED',self.found(base64.encodebytes(json.dumps({'document':self.value}).encode())))
    def test_mime_wrapped_base64_in_json_string(self):self.assertIn('RESTRICTED',self.found(json.dumps({'attachment':base64.encodebytes(json.dumps({'document':self.value}).encode()).decode()}).encode()))
    def test_url_full_percent_encoding(self):self.assertIn('RESTRICTED',self.found(''.join('%%%02X'%x for x in self.value.encode()).encode()))
    def test_json_ascii_escapes(self):self.assertIn('RESTRICTED',self.found(''.join('\\u%04x'%ord(x) for x in self.value).encode()))
    def test_hexadecimal(self):self.assertIn('RESTRICTED',self.found(self.value.encode().hex().encode()))
    def test_html_entities(self):self.assertIn('RESTRICTED',self.found(''.join('&#%d;'%ord(x) for x in self.value).encode()))
    def test_no_unknown_secret_claim(self):self.assertEqual(set(),self.found(b'unknown confidential value not seeded in this test'))
    def test_token_limit_not_silent(self):
        data=b' '.join(('UNIQUE_SYNTHETIC_LONG_TOKEN_%04d'%n).encode() for n in range(70));self.assertFalse(detect(data,self.markers)['analysis_complete_within_supported_limits'])
    def test_size_limit_not_silent(self):self.assertFalse(detect(b'x'*(MAX_FILE+1),self.markers)['analysis_complete_within_supported_limits'])

class CaptureTests(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.m=demo.build(self.root)
    def tearDown(self):self.temp.cleanup()
    def first(self):return audit(self.m,self.root)['cases'][0]
    def rewrite(self,data):
        c=self.m['cases'][0];p=self.root/c['capture_file'];p.write_bytes(data);r=load(self.root/c['receipt_file']);r.update(capture_sha256=hashlib.sha256(data).hexdigest(),capture_bytes=len(data));(self.root/c['receipt_file']).write_text(json.dumps(r))
    def receipt(self,**updates):
        p=self.root/self.m['cases'][0]['receipt_file'];r=load(p);r.update(updates);p.write_text(json.dumps(r))
    def test_safe_cases(self):r=audit(self.m,self.root);self.assertTrue(all(c['result']=='contained_in_capture' for c in r['cases']));self.assertEqual('review_required',r['status'])
    def test_leaky_pipeline_both_sinks(self):
        with tempfile.TemporaryDirectory() as d:
            m=demo.build(d,True);r=audit(m,d);self.assertTrue(all(c['result']=='leak_observed' for c in r['cases']))
    def test_mime_capture_does_not_report_containment(self):
        public=self.m['markers'][0]['value'];restricted=self.m['markers'][1]['value'];encoded=base64.encodebytes(json.dumps({'document':restricted}).encode()).decode()
        self.rewrite(json.dumps({'sentinel':public,'attachment':encoded}).encode());self.assertEqual('leak_observed',self.first()['result'])
    def test_empty_capture_not_contained(self):self.rewrite(b'');self.assertEqual('inconclusive',self.first()['result'])
    def test_missing_execution_sentinel_not_contained(self):self.rewrite(b'{"synthetic":"no-marker"}');self.assertEqual('inconclusive',self.first()['result'])
    def test_missing_positive_control_not_contained(self):(self.root/self.m['cases'][0]['positive_control_file']).unlink();self.assertEqual('inconclusive',self.first()['result'])
    def test_broken_positive_control_not_contained(self):(self.root/self.m['cases'][0]['positive_control_file']).write_text('empty');self.assertEqual('inconclusive',self.first()['result'])
    def test_missing_receipt_not_contained(self):(self.root/self.m['cases'][0]['receipt_file']).unlink();self.assertEqual('inconclusive',self.first()['result'])
    def test_malformed_receipt_not_contained(self):(self.root/self.m['cases'][0]['receipt_file']).write_text('{bad');self.assertEqual('inconclusive',self.first()['result'])
    def test_incomplete_capture_not_contained(self):self.receipt(capture_complete=False);self.assertEqual('inconclusive',self.first()['result'])
    def test_incomplete_execution_not_contained(self):self.receipt(execution_complete=False);self.assertEqual('inconclusive',self.first()['result'])
    def test_zero_events_not_contained(self):self.receipt(event_count=0);self.assertEqual('inconclusive',self.first()['result'])
    def test_boolean_event_count_not_contained(self):self.receipt(event_count=True);self.assertEqual('inconclusive',self.first()['result'])
    def test_wrong_capture_hash_not_contained(self):self.receipt(capture_sha256='0'*64);self.assertEqual('inconclusive',self.first()['result'])
    def test_wrong_byte_count_not_contained(self):self.receipt(capture_bytes=0);self.assertEqual('inconclusive',self.first()['result'])
    def test_wrong_case_binding_not_contained(self):self.receipt(case_id='other-case');self.assertEqual('inconclusive',self.first()['result'])
    def test_wrong_sink_binding_not_contained(self):self.receipt(sink_id='other-sink');self.assertEqual('inconclusive',self.first()['result'])
    def test_future_receipt_not_contained(self):self.receipt(observed_on='2099-01-01');self.assertEqual('inconclusive',self.first()['result'])
    def test_oversized_capture_not_contained(self):self.rewrite(b'x'*(MAX_FILE+1));self.assertEqual('inconclusive',self.first()['result'])
    def test_receipt_failure_preserves_marker_signal(self):
        value=self.m['markers'][1]['value'];public=self.m['markers'][0]['value'];self.rewrite((public+' '+value).encode());self.receipt(capture_complete=False);r=self.first();self.assertEqual('inconclusive',r['result']);self.assertIn('RESTRICTED',r['unapproved_marker_ids'])
    def test_result_excludes_raw_values_and_paths(self):
        s=json.dumps(audit(self.m,self.root))
        for marker in self.m['markers']:self.assertNotIn(marker['value'],s)
        for case in self.m['cases']:
            for key in ('capture_file','positive_control_file','receipt_file'):self.assertNotIn(case[key],s)
    def test_result_binds_exact_manifest(self):
        self.assertEqual(hashlib.sha256(json.dumps(self.m,sort_keys=True,separators=(',',':')).encode()).hexdigest(),audit(self.m,self.root)['manifest_sha256'])
    def test_no_shared_reference_mutations(self):before=copy.deepcopy(self.m);audit(self.m,self.root);self.assertEqual(before,self.m)
    def test_production_manifest_rejected(self):
        self.m['environment']='production'
        with self.assertRaises(ValueError):validate_manifest(self.m)
    def test_non_synthetic_manifest_rejected(self):
        self.m['synthetic_only']=False
        with self.assertRaises(ValueError):validate_manifest(self.m)
    def test_real_secret_marker_shape_rejected(self):
        self.m['markers'][1]['value']='not-a-synthetic-canary'
        with self.assertRaises(ValueError):validate_manifest(self.m)
    def test_duplicate_marker_rejected(self):
        self.m['markers'][1]['id']=self.m['markers'][0]['id']
        with self.assertRaises(ValueError):validate_manifest(self.m)
    def test_overlapping_marker_rejected(self):
        self.m['markers'][1]['value']=self.m['markers'][0]['value']+'EXTRA'
        with self.assertRaises(ValueError):validate_manifest(self.m)
    def test_unknown_sink_rejected(self):
        self.m['cases'][0]['sink_id']='missing'
        with self.assertRaises(ValueError):validate_manifest(self.m)
    def test_all_markers_allowed_not_a_containment_test(self):
        self.m['sinks'][0]['allowed_markers']=['PUBLIC','RESTRICTED']
        with self.assertRaises(ValueError):validate_manifest(self.m)
    def test_missing_required_sentinel_rejected(self):
        self.m['cases'][0]['required_markers']=[]
        with self.assertRaises(ValueError):validate_manifest(self.m)
    def test_path_traversal_and_credentials_rejected(self):
        for value in ('../capture.json','/tmp/capture.json','.env','captures/credentials.json','captures\\x.json','captures/./model.json'):
            self.m['cases'][0]['capture_file']=value
            with self.subTest(path=value):
                with self.assertRaises(ValueError):validate_manifest(self.m)
    def test_symlink_capture_not_opened(self):
        p=self.root/self.m['cases'][0]['capture_file'];p.unlink();p.symlink_to(self.root/self.m['cases'][1]['capture_file']);self.assertEqual('inconclusive',self.first()['result'])
    def test_dry_run_needs_no_capture_root(self):
        p=subprocess.run([sys.executable,str(ROOT/'scripts/canary_audit.py'),'--manifest',str(self.root/'manifest.json'),'--dry-run'],capture_output=True,text=True);self.assertEqual(0,p.returncode);self.assertEqual('dry_run_no_capture_reads',json.loads(p.stdout)['status'])
    def test_cli_preserves_existing_manifest(self):
        p=self.root/'manifest.json';before=p.read_bytes();r=subprocess.run([sys.executable,str(ROOT/'scripts/canary_audit.py'),'--manifest',str(p),'--capture-root',str(self.root),'--out',str(p)],capture_output=True,text=True);self.assertNotEqual(0,r.returncode);self.assertEqual(before,p.read_bytes());self.assertNotIn('Traceback',r.stderr)
    def test_malformed_manifest_cli_has_no_traceback(self):
        p=self.root/'bad.json';p.write_text('[]');r=subprocess.run([sys.executable,str(ROOT/'scripts/canary_audit.py'),'--manifest',str(p),'--dry-run'],capture_output=True,text=True);self.assertNotEqual(0,r.returncode);self.assertNotIn('Traceback',r.stderr)

if __name__=='__main__':unittest.main()
