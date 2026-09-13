#!/usr/bin/env python3
import argparse, hashlib, json, pathlib, sys, datetime

HERE = pathlib.Path(__file__).resolve().parent
CONFIG = json.loads((HERE / 'required-targets.json').read_text(encoding='utf-8'))
SIGNOFF_MILESTONE = '13.3.1'
SIGNOFF_SCHEMA = 'atelier-final-production-signoff-v1'


def stable(v):
    if isinstance(v, list):
        return '[' + ','.join(stable(x) for x in v) + ']'
    if isinstance(v, dict):
        return '{' + ','.join(json.dumps(k, separators=(',', ':')) + ':' + stable(v[k]) for k in sorted(v)) + '}'
    return json.dumps(v, separators=(',', ':'), ensure_ascii=False)


def fingerprint(payload):
    return hashlib.sha256(stable(payload).encode('utf-8')).hexdigest()


def file_sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def validate_file(path):
    errors=[]
    try: original=json.loads(path.read_text(encoding='utf-8'))
    except Exception as e: return None,None,[f'invalid JSON: {e}']
    data=dict(original)
    fp=data.pop('evidenceFingerprint',None)
    if fp != fingerprint(data): errors.append('evidence fingerprint mismatch')
    if original.get('schema')!='atelier-physical-acceptance-evidence-v1': errors.append('unexpected evidence schema')
    if original.get('acceptanceMilestone')!=CONFIG['acceptanceMilestone']: errors.append('acceptance milestone mismatch')
    if original.get('runtimeRelease')!=CONFIG['runtimeRelease']: errors.append('runtime release mismatch')
    if original.get('productionUrl')!=CONFIG['productionUrl']: errors.append('production URL mismatch')
    if original.get('runtimeIndexSha256')!=CONFIG['runtimeIndexSha256']: errors.append('runtime index hash mismatch')
    if original.get('runtimeServiceWorkerSha256')!=CONFIG['runtimeServiceWorkerSha256']: errors.append('runtime service-worker hash mismatch')
    if original.get('attested') is not True: errors.append('tester attestation missing')
    if not str(original.get('tester','')).strip(): errors.append('tester identity missing')
    tid=(original.get('target') or {}).get('id')
    target=next((t for t in CONFIG['targets'] if t['id']==tid),None)
    if not target: errors.append(f'unknown target {tid!r}'); return tid,original,errors
    result_map={r.get('id'):r.get('status') for r in original.get('results',[]) if isinstance(r,dict)}
    for test_id in target['requiredTests']:
        if result_map.get(test_id)!='PASS': errors.append(f'{test_id}: required PASS, got {result_map.get(test_id)!r}')
    return tid,original,errors


def collect(evidence_dir):
    files=sorted(pathlib.Path(evidence_dir).glob('*.json'))
    by_target={}; failures=[]
    for p in files:
        tid,data,errors=validate_file(p)
        if errors: failures.append((p.name,errors))
        elif tid:
            if tid in by_target: failures.append((p.name,[f'duplicate target evidence; already have {by_target[tid]["filename"]}']))
            else:
                by_target[tid]={
                    'filename':p.name,
                    'fileSha256':file_sha256(p),
                    'evidenceFingerprint':data['evidenceFingerprint'],
                    'tester':data.get('tester',''),
                    'deviceModel':data.get('deviceModel',''),
                    'osVersion':data.get('osVersion',''),
                    'browserVersion':data.get('browserVersion',''),
                    'capturedAt':(data.get('environment') or {}).get('timestamp',''),
                }
    required={t['id'] for t in CONFIG['targets']}
    missing=sorted(required-set(by_target))
    ready=not failures and not missing
    return by_target, failures, missing, ready


def build_signoff(by_target):
    target_order=[t['id'] for t in CONFIG['targets']]
    payload={
        'schema':SIGNOFF_SCHEMA,
        'signoffMilestone':SIGNOFF_MILESTONE,
        'acceptanceEvidenceMilestone':CONFIG['acceptanceMilestone'],
        'runtimeRelease':CONFIG['runtimeRelease'],
        'productionUrl':CONFIG['productionUrl'],
        'runtimeIndexSha256':CONFIG['runtimeIndexSha256'],
        'runtimeServiceWorkerSha256':CONFIG['runtimeServiceWorkerSha256'],
        'signoffState':'PASS',
        'requiredTargets':target_order,
        'evidence':[{'targetId':tid,**by_target[tid]} for tid in target_order],
        'generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    out=dict(payload)
    out['signoffFingerprint']=fingerprint(payload)
    return out


def build_report(by_target, failures, missing, ready):
    return {
        'signoffMilestone':SIGNOFF_MILESTONE,
        'acceptanceEvidenceMilestone':CONFIG['acceptanceMilestone'],
        'runtimeRelease':CONFIG['runtimeRelease'],
        'validEvidence':len(by_target),
        'requiredEvidence':len(CONFIG['targets']),
        'failures':[{'filename':name,'errors':errs} for name,errs in failures],
        'missing':missing,
        'signoffReady':ready,
    }


def run(evidence_dir, write_signoff=None, write_report=None):
    by_target,failures,missing,ready=collect(evidence_dir)
    print(f'VALID_EVIDENCE={len(by_target)}/{len(CONFIG["targets"])}')
    for tid in sorted(by_target): print(f'PASS {tid}: {by_target[tid]["filename"]}')
    for name,errs in failures:
        for e in errs: print(f'FAIL {name}: {e}')
    for tid in missing: print(f'PENDING {tid}: evidence missing')
    print('SIGNOFF_READY=' + ('true' if ready else 'false'))
    if write_report:
        pathlib.Path(write_report).write_text(json.dumps(build_report(by_target,failures,missing,ready),indent=2)+'\n',encoding='utf-8')
    if write_signoff:
        if not ready:
            print('SIGNOFF_FILE=not-written (gate blocked)')
        else:
            path=pathlib.Path(write_signoff)
            path.write_text(json.dumps(build_signoff(by_target),indent=2)+'\n',encoding='utf-8')
            print(f'SIGNOFF_FILE={path}')
    return 0 if ready else 2


def fixture_payload(t):
    payload={
      'schema':'atelier-physical-acceptance-evidence-v1','acceptanceMilestone':CONFIG['acceptanceMilestone'],
      'runtimeRelease':CONFIG['runtimeRelease'],'productionUrl':CONFIG['productionUrl'],
      'runtimeIndexSha256':CONFIG['runtimeIndexSha256'],'runtimeServiceWorkerSha256':CONFIG['runtimeServiceWorkerSha256'],
      'target':{'id':t['id'],'label':t['label']},'tester':'CI fixture','deviceModel':'fixture','osVersion':'fixture','browserVersion':'fixture',
      'environment':{'timestamp':'2026-09-13T00:00:00Z'},'results':[{'id':x,'status':'PASS','notes':''} for x in t['requiredTests']],
      'generalNotes':'synthetic validator fixture','attested':True
    }
    out=dict(payload);out['evidenceFingerprint']=fingerprint(payload)
    return out


def self_test():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        d=pathlib.Path(td)
        for t in CONFIG['targets']:
            (d/f'{t["id"]}.json').write_text(json.dumps(fixture_payload(t),indent=2),encoding='utf-8')
        signoff=pathlib.Path(td).parent/(pathlib.Path(td).name+'-signoff.json'); report=pathlib.Path(td).parent/(pathlib.Path(td).name+'-report.json')
        assert run(d,signoff,report)==0
        signed=json.loads(signoff.read_text())
        fp=signed.pop('signoffFingerprint')
        assert fp==fingerprint(signed)
        assert len(signed['evidence'])==len(CONFIG['targets'])
        bad=json.loads((d/'firefox-desktop.json').read_text());bad['results'][0]['status']='FAIL'
        payload={k:v for k,v in bad.items() if k!='evidenceFingerprint'};bad['evidenceFingerprint']=fingerprint(payload)
        (d/'firefox-desktop.json').write_text(json.dumps(bad),encoding='utf-8')
        signoff.unlink()
        assert run(d,signoff,report)==2
        assert not signoff.exists()
        # Duplicate target must block.
        (d/'firefox-copy.json').write_text(json.dumps(fixture_payload(CONFIG['targets'][0])),encoding='utf-8')
        assert run(d)==2
    print('SELF_TEST=PASS')
    return 0

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--evidence-dir')
    ap.add_argument('--write-signoff')
    ap.add_argument('--write-report')
    ap.add_argument('--self-test',action='store_true')
    args=ap.parse_args()
    if args.self_test: sys.exit(self_test())
    if not args.evidence_dir: ap.error('--evidence-dir is required unless --self-test is used')
    sys.exit(run(args.evidence_dir,args.write_signoff,args.write_report))
