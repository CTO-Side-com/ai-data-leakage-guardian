"""Rebuild a synthetic offline demonstration; never contacts an AI service."""
from pathlib import Path
import importlib.util
import shutil
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/ai-data-leakage-guardian'
sys.path.insert(0,str(SKILL/'scripts'))
from guardian import initialize,load,write,output,report,tasks,plan,today
from canary_audit import audit
spec=importlib.util.spec_from_file_location('synthetic_pipeline',SKILL/'assets/demo_pipeline.py')
demo=importlib.util.module_from_spec(spec);spec.loader.exec_module(demo)
out=ROOT/'docs/example';out.mkdir(parents=True,exist_ok=True)
observations={}
for name,leaky in [('safe',False),('leaky',True)]:
    with tempfile.TemporaryDirectory() as temp:
        manifest=demo.build(temp,leaky);result=audit(manifest,temp);observations[name]=result
        for path in Path(temp).rglob('*'):
            if path.is_file():output(out/(name+'-run')/path.relative_to(temp)).write_bytes(path.read_bytes())
        write(out/(name+'-observations.json'),result,True)
if any(c['result']!='contained_in_capture' for c in observations['safe']['cases']):raise RuntimeError('Synthetic safe fixture failed its scoped checks')
if any(c['result']!='leak_observed' for c in observations['leaky']['cases']):raise RuntimeError('Synthetic leaky fixture did not reproduce expected canary observations')

assessment=load(SKILL/'assets/assessment-example.json')
assessment['assessor']='Automated offline synthetic demonstration; no customer application, provider or human approval was assessed'
assessment['evidence']=[]
for eid,scope in [('MODEL-LEAK','model_request'),('TRACE-LEAK','telemetry')]:
    assessment['evidence'].append({'id':eid,'kind':'test','ref':'docs/example/leaky-observations.json',
        'method':'Owned offline fixture produced payloads and receipts; exact known canaries were observed under a synthetic destination policy',
        'reviewer':'Automated synthetic demonstration','environment':'local','scope':'Synthetic '+scope+' capture only',
        'observed_on':today(),'positive_control':'All seeded markers found by the same detector and allowed execution sentinel present',
        'negative_case':'Restricted synthetic marker is disallowed at '+scope,'expected':'No restricted seeded marker at this synthetic sink',
        'observed':'Restricted marker was observed with a valid case-bound receipt in the deliberately leaky fixture',
        'data_scope':'Synthetic public and restricted fields only','sink_scope':'The '+scope+' fixture capture; no real transmission occurred','result':'leak_observed'})
assessment['sinks'].append({'id':'telemetry','kind':'observability','location_ref':'synthetic-telemetry-boundary',
    'purpose':'Synthetic trace creation only','approval_status':'approved','approved_data_classes':['public_synthetic'],
    'reviewer':'Synthetic example policy owner','approval_ref':'synthetic-policy:telemetry','retention_evidence_ref':'','training_evidence_ref':''})
assessment['data_flows'].append({'id':'FLOW-TRACE','source':'synthetic pipeline context','sink_id':'telemetry','purpose':'Synthetic telemetry minimization test',
    'data_classes':['restricted_synthetic','public_synthetic'],'transformations':['intended trace-field minimization'],
    'evidence_ref':'skills/ai-data-leakage-guardian/assets/demo_pipeline.py'})
for cid,eid,action in [('PROMPT-003','MODEL-LEAK','Remove the restricted fixture field before constructing the model-bound payload, including encoded attachments.'),('OBS-001','TRACE-LEAK','Allowlist trace fields and redact the restricted fixture field before trace export.')]:
    c=next(c for c in assessment['checks'] if c['id']==cid)
    c.update(status='confirmed_gap',reviewer='Automated synthetic demonstration',
        rationale='Only the deliberately leaky offline fixture violates the supplied synthetic policy; no real model or telemetry service was called.',
        evidence_refs=[eid],severity='high',owner='Synthetic fixture owner',recommendation=action,
        verification_test='Repeat the approved synthetic capture with valid receipts, complete detector-positive controls and an allowed execution sentinel; verify the forbidden canary is absent at this exact sink.')
write(out/'assessment.json',assessment,True);report(assessment,out,True);tasks(assessment,out)
p=out/'TEST-PLAN.md'
if p.exists():p.unlink()
plan(assessment,p)
print('Rebuilt offline synthetic captures, receipts, scoped observations, reports and tasks')
