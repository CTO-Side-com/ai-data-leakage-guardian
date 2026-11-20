"""AI Data Leakage Guardian: offline data-flow evidence, leads and reports."""
import argparse
import copy
import csv
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from datetime import date,datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
NOTICE='Scoped AI data-leakage assessment. Not a guarantee of confidentiality, a production DLP gateway or compliance certification.'
STATES={'insufficient_evidence','suspected_gap','confirmed_gap','verified_in_scope','not_applicable'}
KINDS={'code','configuration','test','operational','architecture'}

def today():return datetime.now(timezone.utc).date().isoformat()
def load(path):
    with Path(path).open(encoding='utf-8') as f:return json.load(f)
def catalog():return load(ROOT/'references/checks.json')
def iso(s):
    if not isinstance(s,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',s):raise ValueError('Use YYYY-MM-DD')
    return date.fromisoformat(s)
def present(v):return isinstance(v,str) and v.strip().upper() not in ('','UNKNOWN','TBD','UNASSIGNED','N/A')
def output(path):
    p=Path(path).absolute()
    if any(x.is_symlink() for x in [p,*p.parents]):raise ValueError('Symlink output paths are refused')
    if p.exists() and p.is_file() and p.stat().st_nlink>1:raise ValueError('Hard-linked output files are refused')
    p.parent.mkdir(parents=True,exist_ok=True);return p
def write(path,data,overwrite=False):
    with output(path).open('w' if overwrite else 'x',encoding='utf-8') as f:json.dump(data,f,indent=2,ensure_ascii=True);f.write('\n')
def clean(s):
    s=str(s).encode('utf-8','replace').decode('utf-8')
    s=re.sub(r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b','[REDACTED_EMAIL]',s)
    s=re.sub(r'\b\d{3}-\d{2}-\d{4}\b','[REDACTED_ID]',s)
    s=re.sub(r'(?i)\b(?:bearer\s+|(?:password|secret|token|api_key)\s*[:=]\s*)[^\s,;]+','[REDACTED_SECRET]',s)
    return s[:20000]
def cell(s):
    s=clean(s).replace('\n',' ').replace('\r',' ')
    return "'"+s if s.lstrip().startswith(('=','+','-','@')) else s
def scrub(x):
    if isinstance(x,dict):return {k:scrub(v) for k,v in x.items()}
    if isinstance(x,list):return [scrub(v) for v in x]
    return clean(x) if isinstance(x,str) else x

def initialize(product,environment):
    if not present(product) or not present(environment):raise ValueError('Product and environment are required')
    return {'schema_version':'1.0','catalog_version':catalog()['version'],'product':product,'environment':environment,
        'created_on':today(),'assessor':'','systems':[],'exclusions':[],'scope_unknowns':[],
        'data_handling_model':'unknown','synthetic_fixture_ref':'','notice':NOTICE,'evidence':[], 'sinks':[], 'data_flows':[],
        'checks':[{'id':c['id'],'status':'insufficient_evidence','reviewer':'','rationale':'','evidence_refs':[],
            'verified_scope':'','approved_by':'','severity':'','owner':'','recommendation':'','verification_test':'',
            'due_date':'','watched_paths':[]} for c in catalog()['checks']]}

def validate(a):
    errors=[]
    def need(ok,msg):
        if not ok:errors.append(msg)
    if not isinstance(a,dict):return ['Assessment must be an object']
    need(a.get('schema_version')=='1.0','Unsupported schema')
    need(a.get('catalog_version')==catalog()['version'],'Catalog version mismatch')
    for k in ('product','environment'):need(present(a.get(k)),'Missing '+k)
    for k in ('assessor','data_handling_model','synthetic_fixture_ref'):need(isinstance(a.get(k),str),k+' must be a string')
    for k in ('systems','exclusions','scope_unknowns'):
        v=a.get(k);need(isinstance(v,list) and all(isinstance(x,str) for x in v),k+' must be a string array')
    sinks=a.get('sinks');flows=a.get('data_flows');sink_ids=set();flow_ids=set()
    if not isinstance(sinks,list) or not isinstance(flows,list):errors.append('sinks and data_flows must be arrays')
    else:
        for sink in sinks:
            if not isinstance(sink,dict) or not present(sink.get('id')):errors.append('Sink needs an id');continue
            sid=sink['id'];need(sid not in sink_ids,'Duplicate sink '+sid);sink_ids.add(sid)
            for key in ('kind','location_ref','purpose','reviewer','approval_ref','retention_evidence_ref','training_evidence_ref'):
                need(isinstance(sink.get(key),str),sid+': '+key+' must be a string')
            need(sink.get('approval_status') in ('unverified','approved','denied'),sid+': invalid approval status')
            classes=sink.get('approved_data_classes')
            need(isinstance(classes,list) and all(present(v) for v in classes),sid+': invalid approved data classes')
            if sink.get('approval_status')=='approved':
                need(present(sink.get('reviewer')) and present(sink.get('approval_ref')),sid+': approval requires reviewer and reference')
        for flow in flows:
            if not isinstance(flow,dict) or not present(flow.get('id')):errors.append('Flow needs an id');continue
            fid=flow['id'];need(fid not in flow_ids,'Duplicate flow '+fid);flow_ids.add(fid)
            for key in ('source','sink_id','purpose','evidence_ref'):need(present(flow.get(key)),fid+': missing '+key)
            sid=flow.get('sink_id');need(isinstance(sid,str) and sid in sink_ids,fid+': unknown sink')
            for key in ('data_classes','transformations'):
                value=flow.get(key);need(isinstance(value,list) and all(present(v) for v in value),fid+': invalid '+key)
    try:need(iso(a.get('created_on'))<=iso(today()),'Future assessment date')
    except (ValueError,TypeError):errors.append('Invalid assessment date')
    evs=a.get('evidence');checks=a.get('checks')
    if not isinstance(evs,list) or not isinstance(checks,list):return errors+['evidence and checks must be arrays']
    evmap={}
    for ev in evs:
        if not isinstance(ev,dict) or not present(ev.get('id')):errors.append('Evidence needs an object with id');continue
        eid=ev['id'];need(eid not in evmap,'Duplicate evidence '+eid);evmap[eid]=ev
        need(isinstance(ev.get('kind'),str) and ev['kind'] in KINDS,eid+': invalid kind')
        for k in ('ref','method','reviewer','environment','scope'):need(present(ev.get(k)),eid+': missing '+k)
        need(ev.get('environment')==a.get('environment'),eid+': environment mismatch')
        try:need(iso(ev.get('observed_on'))<=iso(today()),eid+': future observation')
        except (ValueError,TypeError):errors.append(eid+': invalid observed_on')
        if ev.get('sha256') is not None:need(isinstance(ev['sha256'],str) and bool(re.fullmatch('[a-f0-9]{64}',ev['sha256'])),eid+': invalid hash')
        if ev.get('kind')=='test':
            for k in ('positive_control','negative_case','expected','observed','data_scope','sink_scope'):
                need(present(ev.get(k)),eid+': test needs '+k)
            need(ev.get('result') in ('contained_in_capture','leak_observed','inconclusive'),eid+': invalid test result')
    expected={c['id'] for c in catalog()['checks']};seen=set()
    for c in checks:
        if not isinstance(c,dict) or not isinstance(c.get('id'),str):errors.append('Check needs id');continue
        cid=c['id'];need(cid in expected,'Unknown check '+cid);need(cid not in seen,'Duplicate check '+cid);seen.add(cid)
        valid=True
        for k in ('reviewer','rationale','verified_scope','approved_by','severity','owner','recommendation','verification_test','due_date'):
            if not isinstance(c.get(k),str):errors.append(cid+': '+k+' must be a string');valid=False
        refs=c.get('evidence_refs');watch=c.get('watched_paths')
        if not isinstance(refs,list) or any(not isinstance(x,str) for x in refs):errors.append(cid+': invalid evidence_refs');valid=False
        need(isinstance(watch,list) and all(present(x) for x in watch),cid+': invalid watched_paths')
        status=c.get('status')
        if not isinstance(status,str) or status not in STATES:errors.append(cid+': invalid status');valid=False
        if not valid:continue
        need(c['severity'] in ('','critical','high','medium','low'),cid+': invalid severity')
        if c['due_date']:
            try:iso(c['due_date'])
            except ValueError:errors.append(cid+': invalid due_date')
        need(len(refs)==len(set(refs)),cid+': duplicate evidence ref')
        for r in refs:need(r in evmap,cid+': unknown evidence '+r)
        if status!='insufficient_evidence':
            need(present(c['reviewer']),cid+': reviewer required');need(present(c['rationale']),cid+': rationale required')
        if status in ('suspected_gap','confirmed_gap','verified_in_scope'):need(bool(refs),cid+': evidence required')
        if status=='not_applicable':need(present(c['approved_by']),cid+': applicability approval required')
        if status in ('confirmed_gap','suspected_gap'):
            for k in ('severity','owner','recommendation','verification_test'):need(present(c[k]),cid+': gap needs '+k)
        if status=='confirmed_gap':
            evidence=[evmap[r] for r in refs if r in evmap]
            need(any(e.get('kind')!='test' or e.get('result')=='leak_observed' for e in evidence),cid+': contained or inconclusive tests alone cannot establish a confirmed gap')
        if status=='verified_in_scope':
            need(present(c['verified_scope']),cid+': explicit verified_scope required')
            tests=[evmap[r] for r in refs if r in evmap and evmap[r].get('kind')=='test']
            need(bool(tests),cid+': verification requires runtime test evidence')
            need(all(t.get('result')=='contained_in_capture' for t in tests),cid+': only scoped capture tests with complete reviewed controls can verify a tested boundary')
    need(seen==expected,'Missing checks: '+', '.join(sorted(expected-seen)))
    return errors
def require_valid(a):
    errors=validate(a)
    if errors:raise ValueError('\n'.join(errors))

RULES=[
 ('prompt-in-logs',r'(?i)(logger\.(?:info|debug|error)|logging\.(?:info|debug|error)|console\.(?:log|debug)|print\()[^\n]{0,180}\b(prompt|messages|conversation|chat_history)\b','OBS-001','high'),
 ('request-body-logging',r'(?i)(logger\.(?:info|debug|error)|console\.(?:log|debug)|print\()[^\n]{0,180}\b(request\.body|request\.json|req\.body)\b','OBS-001','high'),
 ('raw-model-output-logging',r'(?i)(logger\.(?:info|debug|error)|console\.(?:log|debug)|print\()[^\n]{0,180}\b(completion|model_response|llm_response|tool_result)\b','OBS-002','medium'),
 ('raw-output-option',r'(?i)\binclude_raw\s*[:=]\s*(True|true)\b','OBS-002','medium'),
 ('sdk-debug-logging',r'(?i)\b(?:OPENAI_LOG|ANTHROPIC_LOG)\s*=\s*[\x27\x22]?(?:debug|trace)','OBS-003','medium'),
 ('unfiltered-vector-query',r'(?i)\b(?:query_filter|filter)\s*=\s*(?:None\b|\{\s*\})','RAG-001','medium'),
 ('prompt-secret-field',r'(?i)\b(?:system_prompt|system_message)\b[^\n]{0,180}\b(api_key|password|secret|access_token)\b','PROMPT-001','high'),
 ('tls-verification-disabled',r'(?i)\b(?:verify\s*=\s*False|rejectUnauthorized\s*:\s*false)\b','EGRESS-003','high'),
 ('sensitive-url-query',r'(?i)[?&](?:email|patient_id|ssn|api_key|access_token|prompt)=','EGRESS-004','high'),
 ('prompt-in-analytics',r'(?i)\b(?:analytics|telemetry)\.(?:track|capture|record)\([^\n]{0,180}\b(prompt|messages|conversation)\b','OBS-004','high'),
 ('raw-tool-response',r'(?i)\b(?:return|content\s*[:=])[^\n]{0,140}\b(?:tool_result|raw_result|database_result)\b','TOOL-002','medium'),
 ('provider-training-file',r'(?i)\b(?:purpose\s*[:=]\s*[\x27\x22]fine-tune[\x27\x22]|training_file\s*[:=])','LIFE-002','medium')]

SKIP={'.git','.venv','venv','node_modules','__pycache__','dist','build','data','datasets','uploads','records','logs','backups','fixtures','samples','leakage-output'}
SUFFIXES={'.py','.ts','.tsx','.js','.jsx','.sql','.go','.rb','.java','.cs','.php','.tf','.yaml','.yml','.json','.toml'}

def scan(repo,max_files=10000,max_bytes=524288,max_findings=1000):
    import os
    if min(max_files,max_bytes,max_findings)<1:raise ValueError('Limits must be positive')
    repo=Path(repo).resolve(strict=True)
    if not repo.is_dir():raise ValueError('Repository must be a directory')
    leads=[];count=0;ignored=0;limit=False
    compiled=[(rid,re.compile(pat),cid,sev) for rid,pat,cid,sev in RULES]
    for base,dirs,files in os.walk(repo,followlinks=False):
        dirs[:]=sorted(d for d in dirs if d not in SKIP and not (Path(base)/d).is_symlink() and (Path(base)/d).resolve()!=ROOT)
        for name in sorted(files):
            p=Path(base)/name
            if p.is_symlink() or name.startswith('.env') or name.lower() in {'credentials.json','secrets.json','service-account.json','auth.json','token.json'} or p.suffix.lower() not in SUFFIXES:continue
            if count>=max_files:limit=True;break
            count+=1
            if p.stat().st_size>max_bytes:ignored+=1;continue
            try:
                data=p.read_bytes()
                if b'\x00' in data:continue
                text=data.decode('utf-8','replace')
            except OSError:ignored+=1;continue
            for line_number,line in enumerate(text.splitlines(),1):
                for rid,pattern,cid,severity in compiled:
                    if pattern.search(line):
                        path=p.relative_to(repo).as_posix()
                        leads.append({'id':'LEAD-'+hashlib.sha256((rid+'|'+path+'|'+str(line_number)).encode()).hexdigest()[:12],
                            'rule':rid,'check_id':cid,'file':path,'line':line_number,'severity_hint':severity,'status':'unconfirmed_lead'})
                        if len(leads)>=max_findings:limit=True;break
                if limit:break
            if limit:break
        if limit:break
    return {'schema_version':'1.0','scanned_on':today(),'files_considered':count,'files_skipped':ignored,'limit_reached':limit,
        'notice':'Heuristic leads only. Provider calls, raw-output options and training-file references can be intentional. Trace actual data classification, destination authorization and runtime settings before recording a finding.', 'findings':leads}

def plan(a,path):
    require_valid(a)
    lines=['# AI data leakage regression plan',NOTICE,'',
        'Use only independently seeded synthetic canaries and approved offline captures. Do not send real sensitive data to any model, tool, telemetry service or scanner.',
        'Product: '+a['product'],'Environment: '+a['environment'],'Data-handling model: '+a['data_handling_model'],
        'Systems: '+(', '.join(a['systems']) or 'Unknown'),'Exclusions: '+(', '.join(a['exclusions']) or 'None recorded'),
        'Unknowns: '+(', '.join(a['scope_unknowns']) or 'None recorded'),
        'Catalog prompts require adaptation to actual source/transform/sink flows. No endpoints or provider settings are inferred.','']
    for c in catalog()['checks']:
        lines.extend(['## '+c['id']+' | '+c['title'],'Expected boundary: '+c['objective'],'Suggested test: '+c['test'],
            'Record: data class, source, transformations, destination, authorization, observation completeness, positive controls, execution receipt and reviewer.',''])
    with output(path).open('x',encoding='utf-8') as f:f.write('\n'.join(clean(x) for x in lines))

def report(a,out,pdf=False):
    require_valid(a);defs={c['id']:c for c in catalog()['checks']}
    lines=['# AI Data Leakage Guardian',NOTICE,'','Product: '+a['product'],'Environment: '+a['environment'],
        'Assessor: '+(a['assessor'] or 'Unassigned'),'Data-handling model: '+a['data_handling_model'],
        'Systems: '+(', '.join(a['systems']) or 'Unknown'),'Exclusions: '+(', '.join(a['exclusions']) or 'None recorded'),
        'Scope unknowns: '+(', '.join(a['scope_unknowns']) or 'None recorded; scope completeness is not established.'),'',
        '## Source-to-destination register']
    for sink in a['sinks']:
        lines.append('Sink '+sink['id']+' | '+sink['kind']+' | '+sink['approval_status']+' | '+sink['purpose']+
            ' | Retention evidence: '+(sink['retention_evidence_ref'] or 'Unknown')+' | Training-use evidence: '+(sink['training_evidence_ref'] or 'Unknown'))
    for flow in a['data_flows']:
        lines.append(flow['id']+' | '+flow['source']+' -> '+', '.join(flow['transformations'])+' -> '+flow['sink_id']+' | Data classes: '+', '.join(flow['data_classes'])+' | Evidence: '+flow['evidence_ref'])
    if not a['sinks'] or not a['data_flows']:lines.append('The source-to-destination inventory is incomplete; no missing entries are inferred safe.')
    lines.extend(['','## Confirmed findings and suspected gaps'])
    gaps=[c for c in a['checks'] if c['status'] in ('confirmed_gap','suspected_gap')]
    ranks={'critical':0,'high':1,'medium':2,'low':3,'':4}
    for c in sorted(gaps,key=lambda c:(c['status']!='confirmed_gap',ranks[c['severity']])):
        lines.append(c['id']+' | '+c['status']+' | '+c['severity']+' | '+defs[c['id']]['title']+' | '+c['recommendation'])
    if not gaps:lines.append('No findings recorded. Unobserved flows and destinations remain unassessed.')
    lines.extend(['','## Assessment matrix'])
    for c in a['checks']:
        lines.extend(['','### '+c['id']+' | '+defs[c['id']]['title'],'Status: '+c['status'],
            'Rationale: '+(c['rationale'] or 'No supported conclusion recorded.'),
            'Verified scope: '+(c['verified_scope'] or 'None'),
            'Evidence: '+(', '.join(c['evidence_refs']) or 'None'),
            'Reviewer: '+(c['reviewer'] or 'Unassigned')+'; Owner: '+(c['owner'] or 'Unassigned'),
            'Next action: '+(c['recommendation'] or 'Collect scoped evidence and execute an authorized negative test.'),
            'Retest: '+(c['verification_test'] or defs[c['id']]['test'])])
    lines.extend(['','## Evidence index'])
    for e in a['evidence']:lines.append(e['id']+' | '+e['kind']+' | '+e['ref']+' | '+e['scope']+' | '+e['observed_on'])
    lines.extend(['','Counts describe reviewed evidence states, not a confidentiality score. A clean capture does not verify unobserved stages, other providers, retention or future model behavior.',
        'PDF uses built-in Western fonts. Use Markdown for full Unicode. Review all outputs before sharing; redaction is limited.'])
    lines=[clean(x) for x in lines]
    output(Path(out)/'AI-DATA-LEAKAGE.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    write(Path(out)/'assessment-redacted.json',scrub(a),True)
    with output(Path(out)/'risk-register.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(['Check','Title','Status','Severity','Owner','Due','Action','Retest'])
        for c in a['checks']:
            if c['status'] not in ('verified_in_scope','not_applicable'):
                w.writerow([cell(x) for x in [c['id'],defs[c['id']]['title'],c['status'],c['severity'],c['owner'],c['due_date'],c['recommendation'] or 'Collect evidence',c['verification_test'] or defs[c['id']]['test']]])
    if pdf:render_pdf(lines,Path(out)/'AI-DATA-LEAKAGE.pdf')
    names=['AI-DATA-LEAKAGE.md','assessment-redacted.json','risk-register.csv']+(['AI-DATA-LEAKAGE.pdf'] if pdf else [])
    write(Path(out)/'handoff-manifest.json',{'notice':NOTICE,'raw_evidence_included':False,'files':[{'path':n,'sha256':hashlib.sha256((Path(out)/n).read_bytes()).hexdigest()} for n in names]},True)
    return names

def render_pdf(lines,path):
    from pdf_writer import PDF,wrap
    doc=PDF(title='AI Data Leakage Assessment',author='CTOside',subject=NOTICE);y=800
    for text in lines:
        heading=text.startswith('#');size=14 if text.startswith('# ') else 11 if heading else 9
        if not text:y+=7;continue
        for line in wrap(text.lstrip('# ') if heading else text,size,540,heading):
            if y+size+6>730:
                doc.add_page();doc.rect(0,0,612,44,fill='#111827');doc.text(36,29,'CTOside / AI Data Leakage Guardian',12,True,color='#FFFFFF')
                doc.line(36,750,576,750,color='#39DDF1');doc.text(36,766,'Scoped evidence only. No blanket confidentiality guarantee.',8,color='#566174');doc.text(545,766,str(len(doc.pages)),8);y=72
            doc.text(36,y,line,size,heading,color='#AE2762' if heading else '#152338');y+=size+5
        y+=3
    output(path).write_bytes(doc.output())

def tasks(a,out):
    require_valid(a);defs={c['id']:c for c in catalog()['checks']};rows=[]
    for c in a['checks']:
        if c['status'] in ('verified_in_scope','not_applicable'):continue
        prefix={'confirmed_gap':'Fix: ','suspected_gap':'Investigate: ','insufficient_evidence':'Collect evidence: '}[c['status']]
        body=(c['recommendation'] or 'Collect scoped evidence; preserve unknowns.')+' Done when: '+(c['verification_test'] or defs[c['id']]['test'])
        rows.append([prefix+defs[c['id']]['title'],body,{'critical':'Highest','high':'High','medium':'Medium','low':'Low','':'Medium'}[c['severity']],c['owner'],c['due_date'],c['id']])
    for name,headers in [('tasks-jira.csv',['Summary','Description','Priority','Owner','Due Date','Labels']),('tasks-notion.csv',['Name','Description','Priority','Owner','Due','Check']),('tasks-slack-list.csv',['Name','Description','Priority','Owner','Due','Check'])]:
        with output(Path(out)/name).open('w',newline='',encoding='utf-8') as f:
            w=csv.writer(f,lineterminator='\n');w.writerow(headers);w.writerows([[cell(x) for x in row] for row in rows])
    text='\n'.join('- [ ] '+clean(r[0])+' ('+r[5]+')\n  '+clean(r[1]) for r in rows)+'\n'
    output(Path(out)/'tasks.md').write_text(text,encoding='utf-8')
    output(Path(out)/'tasks-slack.txt').write_text(text.replace('@','＠').replace('<','‹').replace('>','›'),encoding='utf-8')
    return len(rows)

def recheck(a,paths):
    require_valid(a);new=copy.deepcopy(a);changed=[]
    for p in paths:
        q=PurePosixPath(p)
        if q.is_absolute() or '..' in q.parts:raise ValueError('Use repository-relative changed paths')
    for c in new['checks']:
        watch=c['watched_paths']
        if paths and (not watch or any(PurePosixPath(p).match(w) or p==w for p in paths for w in watch)):
            c['prior_status']=c['status'];c['status']='insufficient_evidence';c['stale_evidence']=c['evidence_refs'];c['evidence_refs']=[];c['verified_scope']='';c['rationale']='Recheck required after relevant changes.';changed.append(c['id'])
    new['recheck']={'performed_on':today(),'changed_files':paths,'invalidated':changed,'notice':'Changes outside Git, operational drift and stale scope assumptions require separate review.'}
    return new

def main():
    p=argparse.ArgumentParser(description=__doc__);subs=p.add_subparsers(dest='command',required=True)
    q=subs.add_parser('init');q.add_argument('--product',required=True);q.add_argument('--environment',required=True);q.add_argument('--out',required=True)
    q=subs.add_parser('scan');q.add_argument('--repo',required=True);q.add_argument('--out',required=True)
    for name in ('validate','plan','report','tasks','recheck'):
        q=subs.add_parser(name);q.add_argument('--assessment',required=True)
        if name!='validate':q.add_argument('--out',required=True)
        if name=='report':q.add_argument('--pdf',action='store_true')
        if name=='recheck':q.add_argument('--changed-files',required=True)
    a=p.parse_args()
    try:
        if a.command=='init':write(a.out,initialize(a.product,a.environment))
        elif a.command=='scan':write(a.out,scan(a.repo))
        else:
            data=load(a.assessment)
            if a.command in ('report','tasks'):
                names=['AI-DATA-LEAKAGE.md','assessment-redacted.json','risk-register.csv','AI-DATA-LEAKAGE.pdf','handoff-manifest.json'] if a.command=='report' else ['tasks-jira.csv','tasks-notion.csv','tasks-slack-list.csv','tasks.md','tasks-slack.txt']
                if any((Path(a.out)/n).resolve()==Path(a.assessment).resolve() or ((Path(a.out)/n).exists() and (Path(a.out)/n).samefile(a.assessment)) for n in names):
                    raise ValueError('Output would replace the source assessment; choose another directory')
            if a.command=='validate':require_valid(data);print('Valid structure. Evidence truth and scope sufficiency require review.')
            elif a.command=='plan':plan(data,a.out)
            elif a.command=='report':report(data,a.out,a.pdf)
            elif a.command=='tasks':print('Exported',tasks(data,a.out),'tasks')
            elif a.command=='recheck':
                if Path(a.out).resolve()==Path(a.assessment).resolve():raise ValueError('Preserve the baseline; choose a new output path')
                paths=[s.strip() for s in Path(a.changed_files).read_text().splitlines() if s.strip()]
                write(a.out,recheck(data,paths))
    except (ValueError,OSError,TypeError,KeyError) as e:p.exit(1,'AI Data Leakage Guardian: '+str(e)+'\n')
if __name__=='__main__':main()
