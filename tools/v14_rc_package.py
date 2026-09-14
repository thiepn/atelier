#!/usr/bin/env python3
"""Package a V14 release-candidate artifact from a validated development build."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

CORE_RE = re.compile(r"const CORE=(\[[^\r\n]*\]);")
CACHE_RE = re.compile(r"const CACHE='([^']+)';")
DEV_STYLE = '<link rel="stylesheet" href="v14/dev-status/dev-status.css">\n'
DEV_MODULE = '<script type="module" src="v14/dev-status/dev-status.js"></script>\n'


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text('utf-8'))
    if not isinstance(value, dict):
        raise ValueError(f'Expected JSON object: {path}')
    return value


def certification_gate(matrix: dict) -> dict:
    final = matrix.get('finalSignoff') or {}
    evidence = matrix.get('evidenceInventory') or {}
    blockers: list[str] = []
    if final.get('state') != 'pass':
        blockers.append('prior-final-signoff-not-pass')
    if final.get('runtimeMayAdvanceToV14') is not True:
        blockers.append('runtime-advance-not-authorized')
    valid = evidence.get('valid')
    required = evidence.get('required')
    if not isinstance(valid, int) or not isinstance(required, int) or valid < required:
        blockers.append('physical-evidence-incomplete')
    return {
        'sourceMilestone': matrix.get('signoffMilestone'),
        'priorRuntime': matrix.get('runtimeRelease'),
        'priorFinalSignoff': final.get('state'),
        'runtimeMayAdvanceToV14': final.get('runtimeMayAdvanceToV14') is True,
        'physicalEvidence': {'valid': valid, 'required': required},
        'promotionEligible': not blockers,
        'blockers': blockers,
    }


def package(repo_root: Path, source_dir: Path, output_dir: Path, force: bool = False, require_eligible: bool = False) -> dict:
    repo_root = repo_root.resolve()
    source_dir = source_dir.resolve()
    output_dir = output_dir.resolve()
    if not source_dir.is_dir():
        raise ValueError(f'Missing development artifact: {source_dir}')
    if output_dir.exists():
        if not force:
            raise ValueError(f'Output directory already exists: {output_dir}; use --force to replace it')
        shutil.rmtree(output_dir)
    shutil.copytree(source_dir, output_dir)

    build_path = output_dir / 'v14-build-manifest.json'
    build = load_json(build_path)
    version = build.get('version')
    if not isinstance(version, str) or not version.startswith('14.0.0-dev.'):
        raise ValueError('RC packaging requires a V14 development build')

    matrix = load_json(repo_root / 'CERTIFICATION_MATRIX_13.3.1.json')
    gate = certification_gate(matrix)
    if require_eligible and not gate['promotionEligible']:
        raise ValueError('Production eligibility blocked: ' + ', '.join(gate['blockers']))

    index_path = output_dir / 'index.html'
    html = index_path.read_text('utf-8')
    if html.count(DEV_STYLE) != 1 or html.count(DEV_MODULE) != 1:
        raise ValueError('Expected exactly one development-diagnostics style and module tag')
    html = html.replace(DEV_STYLE, '').replace(DEV_MODULE, '')
    index_path.write_text(html, 'utf-8')

    for relative in ('v14/dev-status/dev-status.css', 'v14/dev-status/dev-status.js'):
        path = output_dir / relative
        if not path.is_file():
            raise ValueError(f'Missing development diagnostics asset: {relative}')
        path.unlink()
    dev_dir = output_dir / 'v14/dev-status'
    if dev_dir.exists() and not any(dev_dir.iterdir()):
        dev_dir.rmdir()

    sw_path = output_dir / 'sw.js'
    worker = sw_path.read_text('utf-8')
    cache_match = CACHE_RE.search(worker)
    core_match = CORE_RE.search(worker)
    if not cache_match or not core_match:
        raise ValueError('Generated service worker is missing CACHE or CORE declaration')
    dev_cache = cache_match.group(1)
    expected_dev_cache = 'atelier-v14-dev-' + version
    if dev_cache != expected_dev_cache:
        raise ValueError(f'Unexpected development cache: {dev_cache}')
    rc_cache = 'atelier-v14-rc-' + version
    worker = worker.replace("const CACHE='" + dev_cache + "';", "const CACHE='" + rc_cache + "';", 1)
    worker = worker.replace("k.startsWith('atelier-v14-dev-')", "k.startsWith('atelier-v14-rc-')")
    core = ast.literal_eval(core_match.group(1))
    for asset in ('./v14/dev-status/dev-status.css', './v14/dev-status/dev-status.js'):
        if asset not in core:
            raise ValueError(f'Development diagnostics asset missing from service-worker core: {asset}')
        core.remove(asset)
    worker = CORE_RE.sub('const CORE=' + json.dumps(core, separators=(',', ':')) + ';', worker, count=1)
    sw_path.write_text(worker, 'utf-8')

    build['artifactKind'] = 'release-candidate'
    build['developmentOnly'] = False
    build['productionEligible'] = gate['promotionEligible']
    build['diagnosticsStripped'] = True
    build['certificationGate'] = gate
    build['artifact']['indexSha256'] = sha256(index_path.read_bytes())
    build['artifact']['bytes'] = index_path.stat().st_size
    sw = build.get('serviceWorker') or {}
    sw['outputSha256'] = sha256(sw_path.read_bytes())
    sw['cache'] = rc_cache
    sw['cachePrefix'] = 'atelier-v14-rc-'
    sw['core'] = core
    build['serviceWorker'] = sw
    build_path.write_text(json.dumps(build, indent=2) + '\n', 'utf-8')

    status = {
        'schema': 'atelier-v14-release-candidate-status-v1',
        'version': version,
        'artifactKind': 'release-candidate',
        'diagnosticsStripped': True,
        'productionEligible': gate['promotionEligible'],
        'certificationGate': gate,
        'indexSha256': build['artifact']['indexSha256'],
        'serviceWorkerSha256': sw['outputSha256'],
        'cache': rc_cache,
    }
    (output_dir / 'v14-rc-status.json').write_text(json.dumps(status, indent=2) + '\n', 'utf-8')
    return status


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', default='.')
    parser.add_argument('--source-dir', default='v14-dist')
    parser.add_argument('--output-dir', default='v14-rc')
    parser.add_argument('--force', action='store_true')
    parser.add_argument('--require-production-eligible', action='store_true')
    args = parser.parse_args()
    try:
        result = package(Path(args.repo_root), Path(args.source_dir), Path(args.output_dir), args.force, args.require_production_eligible)
        print('V14_RC_PACKAGE_OK=true version=' + result['version'] + ' production_eligible=' + str(result['productionEligible']).lower() + ' blockers=' + ','.join(result['certificationGate']['blockers']))
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError, SyntaxError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
