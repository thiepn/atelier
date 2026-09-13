#!/usr/bin/env python3
import hashlib, json, pathlib, subprocess, sys, tempfile, importlib.util

ROOT=pathlib.Path(__file__).resolve().parents[1]
ACC=ROOT/'acceptance'
INDEX_SHA='561d258b10835af1a8dc6719ce411cd05eff53e31713bc73fb733169649cfc46'
SW_SHA='e8767e445516647851fe5053a3b5c9dd140e0c04ecc719fbfe5eb801094f5236'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def check(cond,name):
    if not cond: raise AssertionError(name)
    print('PASS',name)

check(sha(ROOT/'index.html')==INDEX_SHA,'frozen index hash')
check(sha(ROOT/'sw.js')==SW_SHA,'frozen service worker hash')
center=(ACC/'SIGNOFF_CENTER_13.3.1.html').read_text(encoding='utf-8')
core=(ACC/'signoff_core_13.3.1.js').read_text(encoding='utf-8')
ui=(ACC/'signoff_ui_13.3.1.js').read_text(encoding='utf-8')
check("sm:'13.3.1'" in core,'signoff milestone')
check("am:'13.3.0'" in core,'acceptance evidence compatibility')
check('atelier-final-production-signoff-v1' in core,'final signoff schema')
check('signoff_core_13.3.1.js' in center and 'signoff_ui_13.3.1.js' in center,'signoff modules referenced')
for tid in ['firefox-desktop','safari-macos','safari-ios-iphone','safari-ipados-ipad','chrome-android-installed-pwa']:
    check(tid in core,f'target {tid}')

subprocess.run([sys.executable,str(ACC/'validate_acceptance.py'),'--self-test'],check=True)

spec=importlib.util.spec_from_file_location('validator',ACC/'validate_acceptance.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
with tempfile.TemporaryDirectory() as td:
    d=pathlib.Path(td)
    report=d.parent/(d.name+'-report.json'); signoff=d.parent/(d.name+'-signoff.json')
    # Empty physical evidence set must remain blocked.
    rc=v.run(d,signoff,report)
    check(rc==2,'empty evidence blocks signoff')
    check(not signoff.exists(),'blocked gate emits no signoff')
    # Complete synthetic set must produce a fingerprinted final manifest.
    for t in v.CONFIG['targets']:
        (d/f'{t["id"]}.json').write_text(json.dumps(v.fixture_payload(t),indent=2),encoding='utf-8')
    rc=v.run(d,signoff,report)
    check(rc==0,'complete evidence unlocks signoff')
    signed=json.loads(signoff.read_text(encoding='utf-8'))
    fp=signed.pop('signoffFingerprint')
    check(fp==v.fingerprint(signed),'signoff fingerprint round-trip')
    check(len(signed['evidence'])==5,'five evidence records bound')
print('SIGNOFF_13_3_1_TESTS=PASS')
