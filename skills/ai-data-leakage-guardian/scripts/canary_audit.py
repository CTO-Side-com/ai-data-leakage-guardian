"""Offline inspection of explicitly synthetic, instrumented AI pipeline captures.

No model calls, network, repository execution or real-secret discovery.
"""
import argparse
import base64
import binascii
import hashlib
import html
import json
from pathlib import Path,PurePosixPath
import re
import urllib.parse
from guardian import iso,load,present,today,write,output

MAX_FILE=1048576
MAX_VIEWS=128
MAX_TOTAL=8*1048576

def digest(data):return hashlib.sha256(data).hexdigest()
def relative(value):
    if not isinstance(value,str) or not value or '\\' in value or any(ord(c)<32 for c in value):raise ValueError('Invalid capture path')
    p=PurePosixPath(value)
    if p.is_absolute() or any(x in ('.','..') for x in value.split('/')) or any(x.startswith('.') for x in p.parts):raise ValueError('Use safe relative capture paths')
    if p.name.lower() in {'credentials.json','auth.json','secrets.json','token.json','service-account.json'}:raise ValueError('Credential-file paths are excluded')
    return p

def validate_manifest(m):
    if not isinstance(m,dict) or m.get('schema_version')!='1.0':raise ValueError('Unsupported capture manifest')
    if m.get('synthetic_only') is not True or m.get('environment') not in ('local','test','staging'):raise ValueError('Only synthetic local/test/staging captures are supported')
    for key in ('scenario_id','policy_ref','policy_reviewer'):
        if not present(m.get(key)):raise ValueError('Manifest needs '+key)
    markers=m.get('markers');sinks=m.get('sinks');cases=m.get('cases')
    if not isinstance(markers,list) or not 2<=len(markers)<=32:raise ValueError('Provide 2 to 32 synthetic markers')
    if not isinstance(sinks,list) or not 1<=len(sinks)<=32:raise ValueError('Provide 1 to 32 destination policies')
    if not isinstance(cases,list) or not 1<=len(cases)<=64:raise ValueError('Provide 1 to 64 capture cases')
    mids=set();values=set();sinkmap={};cids=set()
    def label(v):return isinstance(v,str) and re.fullmatch('[A-Za-z0-9_-]{1,80}',v)
    for marker in markers:
        if not isinstance(marker,dict) or not label(marker.get('id')) or marker['id'] in mids:raise ValueError('Invalid or duplicate marker id')
        value=marker.get('value')
        if not isinstance(value,str) or not re.fullmatch('ADLG_CANARY_[A-Za-z0-9_-]{20,116}',value) or value in values:raise ValueError('Use distinct synthetic canary values with ADLG_CANARY_ prefix')
        if not present(marker.get('classification')):raise ValueError('Marker needs classification')
        mids.add(marker['id']);values.add(value)
    if any(a!=b and (a in b or b in a) for a in values for b in values):raise ValueError('Synthetic markers must not overlap')
    for sink in sinks:
        if not isinstance(sink,dict) or not label(sink.get('id')) or sink['id'] in sinkmap:raise ValueError('Invalid or duplicate sink id')
        ids=sink.get('allowed_markers')
        if not isinstance(ids,list) or any(not isinstance(i,str) or i not in mids for i in ids) or len(set(ids))!=len(ids):raise ValueError('Invalid allowed marker set')
        if not present(sink.get('approval_ref')):raise ValueError('Sink policy needs approval reference')
        sinkmap[sink['id']]=sink
    for case in cases:
        if not isinstance(case,dict) or not label(case.get('id')) or case['id'] in cids:raise ValueError('Invalid or duplicate case id')
        sid=case.get('sink_id')
        if not isinstance(sid,str) or sid not in sinkmap:raise ValueError('Case references unknown sink')
        for key in ('capture_file','positive_control_file','receipt_file'):relative(case.get(key))
        needed=case.get('required_markers')
        if not isinstance(needed,list) or not needed or any(not isinstance(x,str) or x not in sinkmap[sid]['allowed_markers'] for x in needed) or len(needed)!=len(set(needed)):
            raise ValueError('Each case needs at least one allowed execution sentinel')
        if set(sinkmap[sid]['allowed_markers'])==mids:raise ValueError('Include at least one forbidden marker for a containment test')
        cids.add(case['id'])
    return m

def detect(data,markers):
    """Bounded exact-canary detection across common transport representations."""
    work=[(data[:MAX_FILE],'literal',0)];seen=set();used=0;limited=len(data)>MAX_FILE;matches={}
    position=0
    while position<len(work):
        value,transform,depth=work[position];position+=1
        sha=digest(value)
        if sha in seen:continue
        if len(seen)>=MAX_VIEWS or used+len(value)>MAX_TOTAL:limited=True;break
        seen.add(sha);used+=len(value)
        for marker in markers:
            if marker['value'].encode() in value:matches.setdefault(marker['id'],set()).add(transform)
        if depth>=2:continue
        candidates=[]
        text=value.decode('utf-8','replace')
        if '%' in text:
            decoded=urllib.parse.unquote_to_bytes(text)
            if decoded!=value:candidates.append((decoded,transform+'/url'))
        if '&' in text:
            decoded=html.unescape(text).encode()
            if decoded!=value:candidates.append((decoded,transform+'/html'))
        if b'\\u00' in value:
            decoded=re.sub(rb'\\u00([0-9A-Fa-f]{2})',lambda m:bytes([int(m.group(1),16)]),value)
            if decoded!=value:candidates.append((decoded,transform+'/json-ascii'))
        if text.lstrip().startswith(('{','[','"')):
            try:
                stack=[json.loads(text)];nodes=0;strings=0
                while stack:
                    node=stack.pop();nodes+=1
                    if nodes>2048 or strings>=128:limited=True;break
                    if isinstance(node,str):candidates.append((node.encode(),transform+'/json-string'));strings+=1
                    elif isinstance(node,dict):stack.extend(node.values())
                    elif isinstance(node,list):stack.extend(node)
            except RecursionError:limited=True
            except (ValueError,UnicodeError):pass
        # MIME transport can wrap a single base64 value across lines. Decode
        # complete consecutive standard-base64 line runs before token scans.
        block=[]
        def flush_block():
            if len(block)>=2:
                try:
                    decoded=base64.b64decode(b''.join(block),validate=True)
                    if decoded:candidates.append((decoded,transform+'/mime-base64'))
                except (binascii.Error,ValueError):pass
            block.clear()
        for line in value.splitlines():
            line=line.strip()
            if re.fullmatch(rb'[A-Za-z0-9+/]{2,76}={0,2}',line):block.append(line)
            else:flush_block()
        flush_block()
        tokens=list(re.finditer(rb'[A-Za-z0-9_+/-]{24,}={0,2}',value))
        if len(tokens)>64:limited=True
        for match in tokens[:64]:
            token=match.group()
            if len(token)>MAX_FILE:limited=True;continue
            try:
                decoded=base64.b64decode(token+b'='*((-len(token))%4),altchars=b'-_',validate=True)
                if decoded:candidates.append((decoded,transform+'/base64'))
            except (binascii.Error,ValueError):pass
            if len(token)%2==0 and re.fullmatch(rb'[0-9A-Fa-f]{48,}',token):
                candidates.append((bytes.fromhex(token.decode()),transform+'/hex'))
        for decoded,name in candidates:
            if len(work)>=MAX_VIEWS or len(decoded)>MAX_FILE:limited=True;continue
            work.append((decoded,name,depth+1))
    return {'matches':[{'marker_id':key,'transforms':sorted(value)} for key,value in sorted(matches.items())],
        'analysis_complete_within_supported_limits':not limited,'views_examined':len(seen),
        'limits_notice':'Exact seeded markers only; at most two decode layers, 64 tokens per view and bounded views/bytes. No semantic paraphrase, OCR, encrypted or compressed-content analysis.'}

def read_local(root,name,limit=MAX_FILE):
    p=root/Path(relative(name))
    if any(x.is_symlink() for x in [p,*p.parents]):raise ValueError('symlink_refused')
    if not p.is_file():raise ValueError('capture_artifact_missing')
    if p.stat().st_size>limit:raise ValueError('capture_artifact_oversized')
    with p.open('rb') as f:data=f.read(limit+1)
    if len(data)>limit:raise ValueError('capture_artifact_oversized')
    return data

def receipt_valid(receipt,case,manifest,data):
    if not isinstance(receipt,dict):return False
    if any(receipt.get(key)!=value for key,value in [('case_id',case['id']),('sink_id',case['sink_id']),('scenario_id',manifest['scenario_id']),('capture_sha256',digest(data))]):return False
    if receipt.get('execution_complete') is not True or receipt.get('capture_complete') is not True or receipt.get('synthetic_only') is not True:return False
    if type(receipt.get('event_count')) is not int or receipt['event_count']<1:return False
    if type(receipt.get('capture_bytes')) is not int or receipt['capture_bytes']!=len(data):return False
    if not present(receipt.get('instrumentation_ref')):return False
    try:return iso(receipt.get('observed_on'))<=iso(today())
    except (ValueError,TypeError):return False

def audit(m,root):
    validate_manifest(m);root=Path(root).absolute()
    if any(x.is_symlink() for x in [root,*root.parents]) or not root.is_dir():raise ValueError('Use a real authorized capture root, without symlinks')
    sinks={s['id']:s for s in m['sinks']};ids={x['id'] for x in m['markers']};cases=[]
    for case in m['cases']:
        result={'case_id':case['id'],'sink_id':case['sink_id'],'result':'inconclusive'}
        try:
            capture=read_local(root,case['capture_file']);positive=read_local(root,case['positive_control_file'])
            try:receipt=json.loads(read_local(root,case['receipt_file'],65536))
            except (ValueError,UnicodeError,RecursionError):receipt=None
            hits=detect(capture,m['markers']);control=detect(positive,m['markers'])
            found={x['marker_id'] for x in hits['matches']};positives={x['marker_id'] for x in control['matches']}
            allowed=set(sinks[case['sink_id']]['allowed_markers']);forbidden=found-allowed
            good_receipt=receipt_valid(receipt,case,m,capture)
            good_control=positives==ids and control['analysis_complete_within_supported_limits']
            executed=set(case['required_markers']).issubset(found)
            result.update(capture_sha256=digest(capture),capture_bytes=len(capture),matches=hits['matches'],
                unapproved_marker_ids=sorted(forbidden),receipt_valid=good_receipt,positive_control_valid=good_control,
                execution_sentinel_present=executed,analysis_complete_within_supported_limits=hits['analysis_complete_within_supported_limits'])
            if not good_receipt or not good_control or not executed:result['reason']='Capture provenance, detector positive controls or execution sentinel is incomplete.'
            elif forbidden:result.update(result='leak_observed',reason='A known synthetic marker was observed at a destination that disallows it under the supplied policy.')
            elif not hits['analysis_complete_within_supported_limits']:result['reason']='Analysis limits were reached; no containment conclusion is supported.'
            else:result.update(result='contained_in_capture',reason='No disallowed seeded marker was observed in this specific complete reviewed capture under supported representations.')
        except (ValueError,OSError) as e:
            result['reason']='Capture artifacts unavailable, oversized or unsafe; no supported conclusion.'
            result['error_type']=type(e).__name__
        cases.append(result)
    return {'schema_version':'1.0','observed_on':today(),'environment':m['environment'],'status':'review_required',
        'manifest_sha256':digest(json.dumps(m,sort_keys=True,separators=(',',':')).encode()),'cases':cases,
        'notice':'Offline synthetic capture observations only. Receipt truth, policy authority and instrumentation completeness require human review. No network requests or assessment updates were made.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--manifest',required=True);p.add_argument('--capture-root');p.add_argument('--out');p.add_argument('--dry-run',action='store_true');a=p.parse_args()
    try:
        m=validate_manifest(load(a.manifest))
        if a.dry_run:print(json.dumps({'status':'dry_run_no_capture_reads','cases':len(m['cases']),'markers':len(m['markers']),'environment':m['environment']}));return
        if not a.capture_root or not a.out:raise ValueError('Supply --capture-root and a new --out file')
        if output(a.out).exists():raise ValueError('Choose a new output path')
        write(a.out,audit(m,a.capture_root))
    except (ValueError,OSError,TypeError,KeyError,RecursionError) as e:p.exit(1,'Canary audit: '+type(e).__name__+'; check manifest, scope and capture artifacts.\n')
if __name__=='__main__':main()
