#!/usr/bin/env python3
"""Package the validated V14 RC into an isolated GitHub Pages staging subtree."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse

STAGING_SCHEMA = 'atelier-v14-staging-status-v1'
CONFIG_RE = re.compile(r"const CONFIG=\{.*?\n\};\nconst DEFINITIONS=\{", re.S)
UPDATE_GATE_RE = re.compile(r"function updateGate\(\)\{.*?return ok;\}")
EXPORT_RE = re.compile(r"document\.getElementById\('export'\)\.onclick=async\(\)=>\{.*?\};\ndocument\.getElementById\('reset'\)", re.S)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text('utf-8'))
    if not isinstance(value, dict):
        raise ValueError(f'Expected object: {path}')
    return value


def clean_https_dir(value: str, label: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme != 'https' or not parsed.netloc or parsed.query or parsed.fragment or not parsed.path.endswith('/'):
        raise ValueError(f'{label} must be a clean HTTPS directory URL')
    return value


def candidate_origin(url: str) -> str:
    parsed = urlparse(url)
    return f'{parsed.scheme}://{parsed.netloc}/'


def build_runner(template: str, plan: dict, rc: dict) -> str:
    deployment = plan['candidateDeployment']
    candidate_url = clean_https_dir(deployment['url'], 'candidate URL')
    production_url = clean_https_dir(deployment['productionUrl'], 'production URL')
    if candidate_url == production_url:
        raise ValueError('staging candidate URL must differ from production URL')

    targets = [{'id': t['id'], 'label': t['label'], 'required': t['requiredTests']} for t in plan['targets']]
    config = {
        'milestone': plan['acceptanceMilestone'],
        'evidenceSchema': plan['evidenceSchema'],
        'rcVersion': rc['version'],
        'candidateOrigin': candidate_origin(candidate_url),
        'candidateUrl': candidate_url,
        'runnerUrl': deployment['runnerUrl'],
        'indexSha256': rc['indexSha256'],
        'swSha256': rc['serviceWorkerSha256'],
        'cache': rc['cache'],
        'targets': targets,
    }
    config_js = 'const CONFIG=' + json.dumps(config, separators=(',', ':')) + ';\nconst DEFINITIONS={'
    runner = CONFIG_RE.sub(config_js, template, count=1)
    if runner == template:
        raise ValueError('Unable to replace acceptance CONFIG block')

    runner = runner.replace('<title>Atelier V13.3 Physical Device Acceptance</title>', '<title>Atelier V14 RC Physical Device Acceptance</title>')
    runner = runner.replace('<h1>Atelier V13.3 Physical Device Acceptance</h1>', '<h1>Atelier V14 RC Physical Device Acceptance</h1>')
    runner = runner.replace('Certification milestone 13.3.0 · Runtime frozen at Atelier 13.2.0', f'Physical acceptance · {rc["version"]} · exact staging RC')
    runner = runner.replace('href="https://thiepn.github.io/atelier/"', 'href="app/"')
    runner = runner.replace('Open production Atelier', 'Open staged V14 RC')
    runner = runner.replace('against <strong>https://thiepn.github.io/atelier/</strong>', 'against the exact staged V14 RC identified by this runner')
    runner = runner.replace("const DEFINITIONS={", "const DEFINITIONS={\n 'rc-identity':['RC identity','Confirm the staged RC identity matches this runner and the automatic index/service-worker hash check passes.'],\n 'no-dev-diagnostics':['No development diagnostics','Confirm the V14 DEV diagnostics surface is absent.'],\n 'cache-isolation':['Cache isolation','Confirm the staged app uses the V14 RC cache/worker scope and production remains independently usable.'],")

    update_gate = "function updateGate(){const r=results(),complete=r.length&&r.every(x=>x.status==='PASS'),att=document.getElementById('attest').checked,tester=document.getElementById('tester').value.trim(),device=document.getElementById('device').value.trim(),os=document.getElementById('os').value.trim(),browser=document.getElementById('browser').value.trim();const ok=identityOK&&complete&&att&&tester&&device&&os&&browser;const gate=document.getElementById('gate');gate.textContent=ok?'EVIDENCE READY':'EVIDENCE BLOCKED';gate.className='status '+(ok?'ready':'blocked');document.getElementById('summary').textContent=`${r.filter(x=>x.status==='PASS').length}/${r.length} required checks PASS · identity ${identityOK?'verified':'not verified'}${att?' · attested':''}`;return ok;}"
    runner, count = UPDATE_GATE_RE.subn(update_gate, runner, count=1)
    if count != 1:
        raise ValueError('Unable to replace acceptance gate')

    verification = "let identityOK=false;async function verifyCandidate(){identityOK=false;showEnv();const box=document.getElementById('environment');try{const [indexText,swText]=await Promise.all([fetch('app/index.html',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error('index '+r.status);return r.text()}),fetch('app/sw.js',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error('sw '+r.status);return r.text()})]);const ih=sha256Bytes(new TextEncoder().encode(indexText)),sh=sha256Bytes(new TextEncoder().encode(swText));identityOK=ih===CONFIG.indexSha256&&sh===CONFIG.swSha256;box.textContent=JSON.stringify({candidateUrl:CONFIG.candidateUrl,rcVersion:CONFIG.rcVersion,rcCache:CONFIG.cache,indexSha256:ih,indexExpected:CONFIG.indexSha256,serviceWorkerSha256:sh,serviceWorkerExpected:CONFIG.swSha256,identityVerified:identityOK,environment:env()},null,2);}catch(error){box.textContent='IDENTITY VERIFICATION FAILED\\n'+String(error);}updateGate();}"
    runner = runner.replace("const targetEl=document.getElementById('target'),testsEl=document.getElementById('tests');", verification + "\nconst targetEl=document.getElementById('target'),testsEl=document.getElementById('tests');")
    runner = runner.replace("document.getElementById('refresh').onclick=showEnv;", "document.getElementById('refresh').onclick=verifyCandidate;")

    export_handler = "document.getElementById('export').onclick=async()=>{if(!updateGate()){alert('Identity must verify, all required checks must PASS, device/tester fields must be filled, and attestation must be checked.');return;}const t=CONFIG.targets.find(x=>x.id===targetEl.value);const payload={schema:CONFIG.evidenceSchema,acceptanceMilestone:CONFIG.milestone,rcVersion:CONFIG.rcVersion,rcIndexSha256:CONFIG.indexSha256,rcServiceWorkerSha256:CONFIG.swSha256,rcCache:CONFIG.cache,candidateOrigin:CONFIG.candidateOrigin,candidateUrl:CONFIG.candidateUrl,runnerUrl:CONFIG.runnerUrl,target:{id:t.id,label:t.label},tester:document.getElementById('tester').value.trim(),deviceModel:document.getElementById('device').value.trim(),osVersion:document.getElementById('os').value.trim(),browserVersion:document.getElementById('browser').value.trim(),environment:env(),results:results(),generalNotes:document.getElementById('generalNotes').value.trim(),attested:true};const out={...payload,evidenceFingerprint:await fingerprint(payload)};const blob=new Blob([JSON.stringify(out,null,2)+'\\n'],{type:'application/json'}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=`ATELIER-V14-RC-${t.id}-${new Date().toISOString().slice(0,10)}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);};\ndocument.getElementById('reset')"
    runner, count = EXPORT_RE.subn(export_handler, runner, count=1)
    if count != 1:
        raise ValueError('Unable to replace evidence exporter')
    runner = runner.replace('renderTests();\n</script>', 'renderTests();verifyCandidate();\n</script>')
    return runner


def package(repo_root: Path, rc_dir: Path, output_dir: Path, source_revision: str = '', force: bool = False) -> dict:
    repo_root, rc_dir, output_dir = repo_root.resolve(), rc_dir.resolve(), output_dir.resolve()
    if not rc_dir.is_dir():
        raise ValueError(f'Missing RC artifact: {rc_dir}')
    if output_dir.exists():
        if not force:
            raise ValueError(f'Output already exists: {output_dir}')
        shutil.rmtree(output_dir)
    app_dir = output_dir / 'v14-rc-staging' / 'app'
    app_dir.parent.mkdir(parents=True)
    shutil.copytree(rc_dir, app_dir)

    plan = load_json(repo_root / 'acceptance/v14-rc-required-targets.json')
    rc = load_json(app_dir / 'v14-rc-status.json')
    if rc.get('artifactKind') != 'release-candidate' or rc.get('diagnosticsStripped') is not True:
        raise ValueError('staging requires a stripped release-candidate artifact')
    if sha256(app_dir / 'index.html') != rc['indexSha256']:
        raise ValueError('RC index hash mismatch before staging')
    if sha256(app_dir / 'sw.js') != rc['serviceWorkerSha256']:
        raise ValueError('RC service-worker hash mismatch before staging')

    template = (repo_root / 'acceptance/DEVICE_ACCEPTANCE_13.3.0.html').read_text('utf-8')
    runner = build_runner(template, plan, rc)
    runner_path = output_dir / 'v14-rc-staging' / 'acceptance.html'
    runner_path.write_text(runner, 'utf-8')

    deployment = plan['candidateDeployment']
    status = {
        'schema': STAGING_SCHEMA,
        'version': rc['version'],
        'candidateUrl': deployment['url'],
        'runnerUrl': deployment['runnerUrl'],
        'productionUrl': deployment['productionUrl'],
        'sourceRevision': source_revision or None,
        'rcIndexSha256': rc['indexSha256'],
        'rcServiceWorkerSha256': rc['serviceWorkerSha256'],
        'rcCache': rc['cache'],
        'runnerSha256': sha256(runner_path),
        'productionEligible': rc.get('productionEligible') is True,
        'promotionBlockers': (rc.get('certificationGate') or {}).get('blockers', []),
    }
    (output_dir / 'v14-rc-staging' / 'staging-status.json').write_text(json.dumps(status, indent=2) + '\n', 'utf-8')
    return status


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', default='.')
    parser.add_argument('--rc-dir', default='v14-rc')
    parser.add_argument('--output-dir', default='v14-staging')
    parser.add_argument('--source-revision', default='')
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()
    try:
        result = package(Path(args.repo_root), Path(args.rc_dir), Path(args.output_dir), args.source_revision, args.force)
        print('V14_STAGING_PACKAGE_OK=true version=' + result['version'] + ' candidate=' + result['candidateUrl'])
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
