"""Generate synthetic instrumented captures offline. No model or provider calls."""
import argparse
import base64
import copy
import hashlib
import json
from pathlib import Path
import secrets
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from guardian import load,output,today,write

def build(root,leaky=False):
    root=Path(root).absolute();manifest=copy.deepcopy(load(Path(__file__).with_name('capture-manifest.json')))
    for marker in manifest['markers']:marker['value']='ADLG_CANARY_'+marker['id']+'_'+secrets.token_hex(16)
    values={m['id']:m['value'] for m in manifest['markers']}
    positive={'synthetic_detector_positive':list(values.values())}
    write(root/'controls/detector-positive.json',positive)
    for case in manifest['cases']:
        payload={'synthetic':True,'execution_sentinel':values['PUBLIC'],'restricted':'[REDACTED]'}
        if leaky:
            if case['sink_id']=='model_request':
                payload['attachment_base64']=base64.b64encode(json.dumps({'restricted_synthetic':values['RESTRICTED']}).encode()).decode()
            else:payload['restricted']=values['RESTRICTED']
        data=json.dumps(payload,sort_keys=True).encode()
        capture=output(root/case['capture_file'])
        with capture.open('xb') as f:f.write(data)
        receipt={'scenario_id':manifest['scenario_id'],'case_id':case['id'],'sink_id':case['sink_id'],
            'capture_sha256':hashlib.sha256(data).hexdigest(),'capture_bytes':len(data),'event_count':1,
            'execution_complete':True,'capture_complete':True,'synthetic_only':True,'observed_on':today(),
            'instrumentation_ref':'Owned offline demo_pipeline.py synthetic payload writer; not a live SDK interception'}
        write(root/case['receipt_file'],receipt)
    write(root/'manifest.json',manifest)
    return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--mode',choices=['safe','leaky'],default='safe');a=p.parse_args()
    try:build(a.out,a.mode=='leaky');print('Generated synthetic offline captures; no AI service was contacted.')
    except (ValueError,OSError) as e:p.exit(1,'Synthetic fixture creation failed: '+type(e).__name__+'\n')
