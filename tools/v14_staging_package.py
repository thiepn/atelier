#!/usr/bin/env python3
"""Package a validated V14 RC into an immutable, versioned staging subtree."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse

STAGING_SCHEMA = 'atelier-v14-staging-status-v2'
CONFIG_RE = re.compile(r"const CONFIG=\{.*?\n\};\nconst DEFINITIONS=\{", re.S)
UPDATE_GATE_RE = re.compile(r"function updateGate\(\)\{.*?return ok;\}")
EXPORT_RE = re.compile(r"document\.getElementById\('export'\)\.onclick=async\(\)=>\{.*?\};\ndocument\.getElementById\('reset'\)", re.S)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text('utf-8'))
    if not isinstance(value, dict):
        raise ValueError(f'Expected object: {path}')
    return value


def parse_https_url(value: str, label: str, *, require_directory: bool = False, allow_query: bool = False):
    try:
        parsed = urlparse(value)
    except Exception as exc:
        raise ValueError(f'{label} must be a valid HTTPS URL') from exc
    if parsed.scheme != 'https' or not parsed.netloc or parsed.username is not None or parsed.password is not None:
        raise ValueError(f'{label} must be a valid HTTPS URL')
    if parsed.fragment or (parsed.query and not allow_query):
        raise ValueError(f'{label} contains unsupported query/fragment data')
    if require_directory and not parsed.path.endswith('/'):
        raise ValueError(f'{label} must be a directory URL')
    return parsed


def candidate_origin(url: str) -> str:
    parsed = parse_https_url(url, 'candidate URL', require_directory=True)
    return f'{parsed.scheme}://{parsed.netloc}/'


def expected_candidate_relative_path(version: str) -> str:
    return f'v14-rc-staging/{version}'


def verify_deployment(plan: dict, version: str) -> dict:
    deployment = plan.get('candidateDeployment')
    if not isinstance(deployment, dict):
        raise ValueError('candidateDeployment is required')
    expected_relative = expected_candidate_relative_path(version)
    expected_fragment = f'/atelier/{expected_relative}/'
    candidate = deployment.get('url')
    runner = deployment.get('runnerUrl')
    status = deployment.get('statusUrl')
    production = deployment.get('productionUrl')
    parse_https_url(candidate, 'candidate URL', require_directory=True)
    parse_https_url(runner, 'runner URL', allow_query=True)
    parse_https_url(status, 'status URL')
    parse_https_url(production, 'production URL', require_directory=True)
    if expected_fragment + 'app/' not in candidate:
        raise ValueError('candidate URL is not bound to the current versioned staging path')
    if expected_fragment + 'acceptance.html' not in runner or f'v={version}' not in runner:
        raise ValueError('runner URL is not version-bound and cache-busted')
    if expected_fragment + 'staging-status.json' not in status:
        raise ValueError('status URL is not bound to the current versioned staging path')
    if candidate == production:
        raise ValueError('staging candidate URL must differ from production URL')
    if deployment.get('versionedPathRequired') is not True or deployment.get('preservePriorCandidates') is not True:
        raise ValueError('staging deployment must use immutable versioned paths')
    if deployment.get('runnerCacheBustRequired') is not True:
        raise ValueError('staging runner cache bust is required')
    return deployment


def build_runner(template: str, plan: dict, rc: dict, build: dict, source_revision: str) -> str:
    version = rc['version']
    deployment = verify_deployment(plan, version)
    targets = [{'id': item['id'], 'label': item['label'], 'required': item['requiredTests']} for item in plan['targets']]
    config = {
        'milestone': plan['acceptanceMilestone'],
        'evidenceSchema': plan['evidenceSchema'],
        'rcVersion': version,
        'candidateOrigin': candidate_origin(deployment['url']),
        'candidateUrl': deployment['url'],
        'runnerUrl': deployment['runnerUrl'],
        'stagingStatusUrl': deployment['statusUrl'],
        'productionUrl': deployment['productionUrl'],
        'sourceRevision': source_revision or '',
        'indexSha256': rc['indexSha256'],
        'swSha256': rc['serviceWorkerSha256'],
        'cache': rc['cache'],
        'rcStatusSchema': rc['schema'],
        'ownCacheLookupOnly': bool((build.get('serviceWorker') or {}).get('ownCacheLookupOnly')),
        'targets': targets,
    }
    config_js = 'const CONFIG=' + json.dumps(config, separators=(',', ':')) + ';\nconst DEFINITIONS={'
    runner, count = CONFIG_RE.subn(lambda _: config_js, template, count=1)
    if count != 1:
        raise ValueError('Unable to replace acceptance CONFIG block')

    runner = runner.replace('<title>Atelier V13.3 Physical Device Acceptance</title>', '<title>Atelier V14 RC Physical Device Acceptance</title>')
    runner = runner.replace('<h1>Atelier V13.3 Physical Device Acceptance</h1>', '<h1>Atelier V14 RC Physical Device Acceptance</h1>')
    runner = runner.replace('Certification milestone 13.3.0 · Runtime frozen at Atelier 13.2.0', f'Physical acceptance · {version} · immutable staged RC')
    runner = runner.replace('href="https://thiepn.github.io/atelier/"', f'href="app/?v={version}"')
    runner = runner.replace('Open production Atelier', 'Open staged V14 RC')
    runner = runner.replace('against <strong>https://thiepn.github.io/atelier/</strong>', 'against the exact immutable staged V14 RC identified by this runner')
    runner = runner.replace("const DEFINITIONS={", "const DEFINITIONS={\n 'rc-identity':['RC identity','Automatic verification must confirm this immutable staged URL, raw index/service-worker bytes, RC status metadata and cache identity.'],\n 'no-dev-diagnostics':['No development diagnostics','Confirm the V14 DEV diagnostics surface is absent.'],\n 'cache-isolation':['Cache isolation','Confirm the staged app uses its versioned V14 RC worker/cache and production remains independently usable.'],")

    update_gate = "function updateGate(){const r=results(),complete=r.length&&r.every(x=>x.status==='PASS'),att=document.getElementById('attest').checked,tester=document.getElementById('tester').value.trim(),device=document.getElementById('device').value.trim(),os=document.getElementById('os').value.trim(),browser=document.getElementById('browser').value.trim();const ok=identityOK&&complete&&att&&tester&&device&&os&&browser;const gate=document.getElementById('gate');gate.textContent=ok?'EVIDENCE READY':'EVIDENCE BLOCKED';gate.className='status '+(ok?'ready':'blocked');document.getElementById('summary').textContent=`${r.filter(x=>x.status==='PASS').length}/${r.length} required checks PASS · identity ${identityOK?'verified':'not verified'}${att?' · attested':''}`;return ok;}"
    runner, count = UPDATE_GATE_RE.subn(lambda _: update_gate, runner, count=1)
    if count != 1:
        raise ValueError('Unable to replace acceptance gate')

    verification = """let identityOK=false;
function harnessLocation(){return location.hostname==='127.0.0.1'||location.hostname==='localhost';}
async function rawSha(response){if(!response.ok)throw new Error('HTTP '+response.status+' '+response.url);const bytes=new Uint8Array(await response.arrayBuffer());if(globalThis.crypto?.subtle){const hash=await crypto.subtle.digest('SHA-256',bytes);return [...new Uint8Array(hash)].map(b=>b.toString(16).padStart(2,'0')).join('');}return sha256Bytes(bytes);}
async function verifyCandidate(){identityOK=false;showEnv();const box=document.getElementById('environment');try{const liveLocationOK=harnessLocation()||location.href===CONFIG.runnerUrl;if(!liveLocationOK)throw new Error('Runner URL mismatch: '+location.href);const rev=encodeURIComponent(CONFIG.sourceRevision||CONFIG.rcVersion),q='?v='+encodeURIComponent(CONFIG.rcVersion)+'&r='+rev;const [indexResponse,swResponse,statusResponse]=await Promise.all([fetch('app/index.html'+q,{cache:'no-store'}),fetch('app/sw.js'+q,{cache:'no-store'}),fetch('app/v14-rc-status.json'+q,{cache:'no-store'})]);const [ih,sh]=await Promise.all([rawSha(indexResponse),rawSha(swResponse)]);if(!statusResponse.ok)throw new Error('RC status HTTP '+statusResponse.status);const rs=await statusResponse.json();const statusOK=rs.schema===CONFIG.rcStatusSchema&&rs.version===CONFIG.rcVersion&&rs.artifactKind==='release-candidate'&&rs.diagnosticsStripped===true&&rs.indexSha256===CONFIG.indexSha256&&rs.serviceWorkerSha256===CONFIG.swSha256&&rs.cache===CONFIG.cache;identityOK=liveLocationOK&&CONFIG.ownCacheLookupOnly===true&&statusOK&&ih===CONFIG.indexSha256&&sh===CONFIG.swSha256;box.textContent=JSON.stringify({runnerUrl:CONFIG.runnerUrl,currentRunnerUrl:location.href,candidateUrl:CONFIG.candidateUrl,stagingStatusUrl:CONFIG.stagingStatusUrl,rcVersion:CONFIG.rcVersion,sourceRevision:CONFIG.sourceRevision,rcCache:CONFIG.cache,ownCacheLookupOnly:CONFIG.ownCacheLookupOnly,indexSha256:ih,indexExpected:CONFIG.indexSha256,serviceWorkerSha256:sh,serviceWorkerExpected:CONFIG.swSha256,rcStatusVerified:statusOK,identityVerified:identityOK,environment:env()},null,2);}catch(error){box.textContent='IDENTITY VERIFICATION FAILED\\n'+String(error);}updateGate();}"""
    runner = runner.replace("const targetEl=document.getElementById('target'),testsEl=document.getElementById('tests');", verification + "\nconst targetEl=document.getElementById('target'),testsEl=document.getElementById('tests');")
    runner = runner.replace("document.getElementById('refresh').onclick=showEnv;", "document.getElementById('refresh').onclick=verifyCandidate;")

    export_handler = "document.getElementById('export').onclick=async()=>{if(!updateGate()){alert('Identity must verify, all required checks must PASS, device/tester fields must be filled, and attestation must be checked.');return;}const t=CONFIG.targets.find(x=>x.id===targetEl.value);const payload={schema:CONFIG.evidenceSchema,acceptanceMilestone:CONFIG.milestone,rcVersion:CONFIG.rcVersion,rcIndexSha256:CONFIG.indexSha256,rcServiceWorkerSha256:CONFIG.swSha256,rcCache:CONFIG.cache,candidateOrigin:CONFIG.candidateOrigin,candidateUrl:CONFIG.candidateUrl,runnerUrl:CONFIG.runnerUrl,stagingStatusUrl:CONFIG.stagingStatusUrl,target:{id:t.id,label:t.label},tester:document.getElementById('tester').value.trim(),deviceModel:document.getElementById('device').value.trim(),osVersion:document.getElementById('os').value.trim(),browserVersion:document.getElementById('browser').value.trim(),environment:env(),results:results(),generalNotes:document.getElementById('generalNotes').value.trim(),attested:true};const out={...payload,evidenceFingerprint:await fingerprint(payload)};const blob=new Blob([JSON.stringify(out,null,2)+'\\n'],{type:'application/json'}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=`ATELIER-V14-RC-${CONFIG.rcVersion}-${t.id}-${new Date().toISOString().slice(0,10)}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);};\ndocument.getElementById('reset')"
    runner, count = EXPORT_RE.subn(lambda _: export_handler, runner, count=1)
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

    plan = load_json(repo_root / 'acceptance/v14-rc-required-targets.json')
    rc = load_json(rc_dir / 'v14-rc-status.json')
    build = load_json(rc_dir / 'v14-build-manifest.json')
    version = rc.get('version')
    if not isinstance(version, str) or version != build.get('version'):
        raise ValueError('RC status/build version mismatch')
    deployment = verify_deployment(plan, version)
    if rc.get('artifactKind') != 'release-candidate' or rc.get('diagnosticsStripped') is not True:
        raise ValueError('staging requires a stripped release-candidate artifact')
    sw_record = build.get('serviceWorker') or {}
    if sw_record.get('ownCacheLookupOnly') is not True or sw_record.get('cacheLookupIsolationReplacements') != 3:
        raise ValueError('staging requires an own-cache-only V14 service worker')
    worker_source = (rc_dir / 'sw.js').read_text('utf-8')
    if 'caches.match(' in worker_source:
        raise ValueError('RC worker still contains cross-cache reads')
    if sha256(rc_dir / 'index.html') != rc['indexSha256']:
        raise ValueError('RC index hash mismatch before staging')
    if sha256(rc_dir / 'sw.js') != rc['serviceWorkerSha256']:
        raise ValueError('RC service-worker hash mismatch before staging')

    candidate_root = output_dir / expected_candidate_relative_path(version)
    app_dir = candidate_root / 'app'
    candidate_root.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(rc_dir, app_dir)

    template = (repo_root / 'acceptance/DEVICE_ACCEPTANCE_13.3.0.html').read_text('utf-8')
    runner = build_runner(template, plan, rc, build, source_revision)
    runner_path = candidate_root / 'acceptance.html'
    runner_path.write_text(runner, 'utf-8')

    status = {
        'schema': STAGING_SCHEMA,
        'version': version,
        'candidatePath': expected_candidate_relative_path(version) + '/',
        'candidateUrl': deployment['url'],
        'runnerUrl': deployment['runnerUrl'],
        'statusUrl': deployment['statusUrl'],
        'productionUrl': deployment['productionUrl'],
        'sourceRevision': source_revision or None,
        'rcIndexSha256': rc['indexSha256'],
        'rcServiceWorkerSha256': rc['serviceWorkerSha256'],
        'rcCache': rc['cache'],
        'runnerSha256': sha256(runner_path),
        'immutableCandidatePath': True,
        'priorCandidatesPreserved': True,
        'ownCacheLookupOnly': True,
        'productionEligible': rc.get('productionEligible') is True,
        'promotionBlockers': (rc.get('certificationGate') or {}).get('blockers', []),
    }
    (candidate_root / 'staging-status.json').write_text(json.dumps(status, indent=2) + '\n', 'utf-8')
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
        print('V14_STAGING_PACKAGE_OK=true version=' + result['version'] + ' candidate=' + result['candidateUrl'] + ' immutable=true')
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
