#!/usr/bin/env python3
import argparse, hashlib, json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
CONFIG = json.loads((HERE / 'required-targets.json').read_text(encoding='utf-8'))


def stable(v):
    if isinstance(v, list):
        return '[' + ','.join(stable(x) for x in v) + ']'
    if isinstance(v, dict):
        return '{' + ','.join(json.dumps(k, separators=(',', ':')) + ':' + stable(v[k]) for k in sorted(v)) + '}'
    return json.dumps(v, separators=(',', ':'), ensure_ascii=False)


def fingerprint(payload):
    return hashlib.sha256(stable(payload).encode('utf-8')).hexdigest()


def validate_file(path):
    errors=[]
    try: data=json.loads(path.read_text(encoding='utf-8'))
    except Exception as e: return None,[f'invalid JSON: {e}']
    fp=data.pop('evidenceFingerprint',None)
    if fp != fingerprint(data): errors.append('evidence fingerprint mismatch')
    if data.get('schema')!='atelier-physical-acceptance-evidence-v1': errors.append('unexpected evidence schema')
    if data.get('acceptanceMilestone')!=CONFIG['acceptanceMilestone']: errors.append('acceptance milestone mismatch')
    if data.get('runtimeRelease')!=CONFIG['runtimeRelease']: errors.append('runtime release mismatch')
    if data.get('productionUrl')!=CONFIG['productionUrl']: errors.append('production URL mismatch')
    if data.get('runtimeIndexSha256')!=CONFIG['runtimeIndexSha256']: errors.append('runtime index hash mismatch')
    if data.get('runtimeServiceWorkerSha256')!=CONFIG['runtimeServiceWorkerSha256']: errors.append('runtime service-worker hash mismatch')
    if data.get('attested') is not True: errors.append('tester attestation missing')
    if not str(data.get('tester','')).strip(): errors.append('tester identity missing')
    tid=(data.get('target') or {}).get('id')
    target=next((t for t in CONFIG['targets'] if t['id']==tid),None)
    if not target: errors.append(f'unknown target {tid!r}'); return tid,errors
    result_map={r.get('id'):r.get('status') for r in data.get('results',[]) if isinstance(r,dict)}
    for test_id in target['requiredTests']:
        if result_map.get(test_id)!='PASS': errors.append(f'{test_id}: required PASS, got {result_map.get(test_id)!r}')
    return tid,errors


def run(evidence_dir):
    files=sorted(pathlib.Path(evidence_dir).glob('*.json'))
    by_target={}; failures=[]
    for p in files:
        tid,errors=validate_file(p)
        if errors: failures.append((p.name,errors))
        elif tid:
            if tid in by_target: failures.append((p.name,[f'duplicate target evidence; already have {by_target[tid]}']))
            else: by_target[tid]=p.name
    required={t['id'] for t in CONFIG['targets']}
    missing=sorted(required-set(by_target))
    print(f'VALID_EVIDENCE={len(by_target)}/{len(required)}')
    for tid in sorted(by_target): print(f'PASS {tid}: {by_target[tid]}')
    for name,errs in failures:
        for e in errs: print(f'FAIL {name}: {e}')
    for tid in missing: print(f'PENDING {tid}: evidence missing')
    ready=not failures and not missing
    print('SIGNOFF_READY=' + ('true' if ready else 'false'))
    return 0 if ready else 2


def self_test():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        d=pathlib.Path(td)
        for t in CONFIG['targets']:
            payload={
              'schema':'atelier-physical-acceptance-evidence-v1','acceptanceMilestone':CONFIG['acceptanceMilestone'],
              'runtimeRelease':CONFIG['runtimeRelease'],'productionUrl':CONFIG['productionUrl'],
              'runtimeIndexSha256':CONFIG['runtimeIndexSha256'],'runtimeServiceWorkerSha256':CONFIG['runtimeServiceWorkerSha256'],
              'target':{'id':t['id'],'label':t['label']},'tester':'CI fixture','deviceModel':'fixture','osVersion':'fixture','browserVersion':'fixture',
              'environment':{},'results':[{'id':x,'status':'PASS','notes':''} for x in t['requiredTests']],
              'generalNotes':'synthetic validator fixture','attested':True
            }
            out=dict(payload);out['evidenceFingerprint']=fingerprint(payload)
            (d/f'{t["id"]}.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
        assert run(d)==0
        bad=json.loads((d/'firefox-desktop.json').read_text());bad['results'][0]['status']='FAIL';
        payload={k:v for k,v in bad.items() if k!='evidenceFingerprint'};bad['evidenceFingerprint']=fingerprint(payload)
        (d/'firefox-desktop.json').write_text(json.dumps(bad),encoding='utf-8')
        assert run(d)==2
    print('SELF_TEST=PASS')
    return 0

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--evidence-dir');ap.add_argument('--self-test',action='store_true');args=ap.parse_args()
    if args.self_test: sys.exit(self_test())
    if not args.evidence_dir: ap.error('--evidence-dir is required unless --self-test is used')
    sys.exit(run(args.evidence_dir))
