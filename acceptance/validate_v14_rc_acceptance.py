#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import pathlib
import tempfile
from urllib.parse import urlparse

HERE = pathlib.Path(__file__).resolve().parent
PLAN = json.loads((HERE / 'v14-rc-required-targets.json').read_text(encoding='utf-8'))


def stable(value):
    if isinstance(value, list):
        return '[' + ','.join(stable(x) for x in value) + ']'
    if isinstance(value, dict):
        return '{' + ','.join(json.dumps(k, separators=(',', ':')) + ':' + stable(value[k]) for k in sorted(value)) + '}'
    return json.dumps(value, separators=(',', ':'), ensure_ascii=False)


def fingerprint(payload):
    return hashlib.sha256(stable(payload).encode('utf-8')).hexdigest()


def file_sha256(path):
    digest = hashlib.sha256()
    with pathlib.Path(path).open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def load_rc_status(path):
    status = json.loads(pathlib.Path(path).read_text(encoding='utf-8'))
    errors = []
    if status.get('schema') != PLAN['requiredRcStatusSchema']:
        errors.append('unexpected RC status schema')
    if status.get('artifactKind') != 'release-candidate':
        errors.append('artifactKind must be release-candidate')
    if status.get('diagnosticsStripped') is not True:
        errors.append('RC diagnostics are not marked stripped')
    version = status.get('version')
    if not isinstance(version, str) or not version.startswith('14.0.0-dev.'):
        errors.append('unexpected RC version')
    for key in ('indexSha256', 'serviceWorkerSha256'):
        value = status.get(key)
        if not isinstance(value, str) or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
            errors.append(f'invalid {key}')
    cache = status.get('cache')
    if not isinstance(cache, str) or cache != f'atelier-v14-rc-{version}':
        errors.append('RC cache identity mismatch')
    gate = status.get('certificationGate')
    if not isinstance(gate, dict):
        errors.append('missing RC certificationGate')
    if errors:
        raise ValueError('; '.join(errors))
    return status


def valid_candidate_origin(value):
    try:
        parsed = urlparse(value)
    except Exception:
        return False
    return parsed.scheme == 'https' and bool(parsed.netloc) and parsed.username is None and parsed.password is None


def expected_identity(rc_status):
    return {
        'rcVersion': rc_status['version'],
        'rcIndexSha256': rc_status['indexSha256'],
        'rcServiceWorkerSha256': rc_status['serviceWorkerSha256'],
        'rcCache': rc_status['cache'],
    }


def validate_file(path, rc_status):
    errors = []
    try:
        original = json.loads(pathlib.Path(path).read_text(encoding='utf-8'))
    except Exception as exc:
        return None, None, [f'invalid JSON: {exc}']

    data = dict(original)
    supplied_fingerprint = data.pop('evidenceFingerprint', None)
    if supplied_fingerprint != fingerprint(data):
        errors.append('evidence fingerprint mismatch')
    if original.get('schema') != PLAN['evidenceSchema']:
        errors.append('unexpected evidence schema')
    if original.get('acceptanceMilestone') != PLAN['acceptanceMilestone']:
        errors.append('acceptance milestone mismatch')

    for key, expected in expected_identity(rc_status).items():
        if original.get(key) != expected:
            errors.append(f'{key} mismatch')

    candidate_origin = original.get('candidateOrigin')
    if not valid_candidate_origin(candidate_origin):
        errors.append('candidateOrigin must be an HTTPS origin')
    else:
        parsed = urlparse(candidate_origin)
        normalized = f'{parsed.scheme}://{parsed.netloc}/'
        if candidate_origin != normalized:
            errors.append('candidateOrigin must be normalized to scheme://host[:port]/')

    if original.get('attested') is not True:
        errors.append('tester attestation missing')
    if not str(original.get('tester', '')).strip():
        errors.append('tester identity missing')
    for field in ('deviceModel', 'osVersion', 'browserVersion'):
        if not str(original.get(field, '')).strip():
            errors.append(f'{field} missing')

    target_id = (original.get('target') or {}).get('id')
    target = next((item for item in PLAN['targets'] if item['id'] == target_id), None)
    if not target:
        errors.append(f'unknown target {target_id!r}')
        return target_id, original, errors

    results = original.get('results')
    if not isinstance(results, list):
        errors.append('results must be a list')
        result_map = {}
    else:
        result_map = {}
        for result in results:
            if not isinstance(result, dict):
                errors.append('invalid result entry')
                continue
            result_id = result.get('id')
            if result_id in result_map:
                errors.append(f'duplicate result {result_id!r}')
            result_map[result_id] = result.get('status')

    for test_id in target['requiredTests']:
        if result_map.get(test_id) != 'PASS':
            errors.append(f'{test_id}: required PASS, got {result_map.get(test_id)!r}')

    return target_id, original, errors


def collect(evidence_dir, rc_status):
    files = sorted(pathlib.Path(evidence_dir).glob('*.json'))
    by_target = {}
    failures = []
    candidate_origin = None

    for path in files:
        target_id, data, errors = validate_file(path, rc_status)
        if not errors and data:
            origin = data.get('candidateOrigin')
            if candidate_origin is None:
                candidate_origin = origin
            elif origin != candidate_origin:
                errors.append(f'candidateOrigin differs from previously accepted evidence {candidate_origin}')
        if errors:
            failures.append((path.name, errors))
        elif target_id:
            if target_id in by_target:
                failures.append((path.name, [f'duplicate target evidence; already have {by_target[target_id]["filename"]}']))
            else:
                by_target[target_id] = {
                    'filename': path.name,
                    'fileSha256': file_sha256(path),
                    'evidenceFingerprint': data['evidenceFingerprint'],
                    'tester': data.get('tester', ''),
                    'deviceModel': data.get('deviceModel', ''),
                    'osVersion': data.get('osVersion', ''),
                    'browserVersion': data.get('browserVersion', ''),
                    'capturedAt': (data.get('environment') or {}).get('timestamp', ''),
                    'candidateOrigin': data.get('candidateOrigin', ''),
                }

    required = {target['id'] for target in PLAN['targets']}
    missing = sorted(required - set(by_target))
    physical_ready = not failures and not missing
    return by_target, failures, missing, physical_ready, candidate_origin


def build_physical_signoff(by_target, rc_status, candidate_origin):
    target_order = [target['id'] for target in PLAN['targets']]
    prior_gate_ready = bool(rc_status['certificationGate'].get('promotionEligible'))
    payload = {
        'schema': PLAN['physicalSignoffSchema'],
        'acceptanceMilestone': PLAN['acceptanceMilestone'],
        **expected_identity(rc_status),
        'candidateOrigin': candidate_origin,
        'physicalState': 'PASS',
        'priorReleaseGateReady': prior_gate_ready,
        'promotionReady': prior_gate_ready,
        'requiredTargets': target_order,
        'evidence': [{'targetId': target_id, **by_target[target_id]} for target_id in target_order],
        'generatedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    output = dict(payload)
    output['signoffFingerprint'] = fingerprint(payload)
    return output


def build_report(by_target, failures, missing, physical_ready, candidate_origin, rc_status):
    prior_gate_ready = bool(rc_status['certificationGate'].get('promotionEligible'))
    return {
        'acceptanceMilestone': PLAN['acceptanceMilestone'],
        **expected_identity(rc_status),
        'candidateOrigin': candidate_origin,
        'validEvidence': len(by_target),
        'requiredEvidence': len(PLAN['targets']),
        'failures': [{'filename': name, 'errors': errors} for name, errors in failures],
        'missing': missing,
        'physicalReady': physical_ready,
        'priorReleaseGateReady': prior_gate_ready,
        'promotionReady': physical_ready and prior_gate_ready,
        'priorReleaseBlockers': rc_status['certificationGate'].get('blockers', []),
    }


def run(evidence_dir, rc_status_path, write_signoff=None, write_report=None):
    rc_status = load_rc_status(rc_status_path)
    by_target, failures, missing, physical_ready, candidate_origin = collect(evidence_dir, rc_status)
    prior_gate_ready = bool(rc_status['certificationGate'].get('promotionEligible'))
    promotion_ready = physical_ready and prior_gate_ready

    print(f'VALID_RC_EVIDENCE={len(by_target)}/{len(PLAN["targets"])}')
    for target_id in sorted(by_target):
        print(f'PASS {target_id}: {by_target[target_id]["filename"]}')
    for name, errors in failures:
        for error in errors:
            print(f'FAIL {name}: {error}')
    for target_id in missing:
        print(f'PENDING {target_id}: evidence missing')
    print('PHYSICAL_READY=' + ('true' if physical_ready else 'false'))
    print('PRIOR_RELEASE_GATE_READY=' + ('true' if prior_gate_ready else 'false'))
    print('PROMOTION_READY=' + ('true' if promotion_ready else 'false'))

    if write_report:
        pathlib.Path(write_report).write_text(
            json.dumps(build_report(by_target, failures, missing, physical_ready, candidate_origin, rc_status), indent=2) + '\n',
            encoding='utf-8',
        )
    if write_signoff:
        if not physical_ready:
            print('PHYSICAL_SIGNOFF_FILE=not-written (physical gate blocked)')
        else:
            path = pathlib.Path(write_signoff)
            path.write_text(json.dumps(build_physical_signoff(by_target, rc_status, candidate_origin), indent=2) + '\n', encoding='utf-8')
            print(f'PHYSICAL_SIGNOFF_FILE={path}')

    return 0 if physical_ready else 2


def fixture_payload(target, rc_status, origin='https://rc.example.test/'):
    payload = {
        'schema': PLAN['evidenceSchema'],
        'acceptanceMilestone': PLAN['acceptanceMilestone'],
        **expected_identity(rc_status),
        'candidateOrigin': origin,
        'target': {'id': target['id'], 'label': target['label']},
        'tester': 'CI fixture',
        'deviceModel': 'fixture',
        'osVersion': 'fixture',
        'browserVersion': 'fixture',
        'environment': {'timestamp': '2026-09-14T00:00:00Z'},
        'results': [{'id': test_id, 'status': 'PASS', 'notes': ''} for test_id in target['requiredTests']],
        'generalNotes': 'synthetic validator fixture',
        'attested': True,
    }
    output = dict(payload)
    output['evidenceFingerprint'] = fingerprint(payload)
    return output


def self_test(rc_status_path):
    rc_status = load_rc_status(rc_status_path)
    with tempfile.TemporaryDirectory() as temp_dir:
        root = pathlib.Path(temp_dir)
        for target in PLAN['targets']:
            (root / f'{target["id"]}.json').write_text(json.dumps(fixture_payload(target, rc_status), indent=2), encoding='utf-8')

        signoff = root / 'physical-signoff.json'
        report = root / 'report.json'
        assert run(root, rc_status_path, signoff, report) == 0
        report_data = json.loads(report.read_text(encoding='utf-8'))
        assert report_data['physicalReady'] is True
        assert report_data['promotionReady'] is bool(rc_status['certificationGate'].get('promotionEligible'))
        signed = json.loads(signoff.read_text(encoding='utf-8'))
        signed_payload = dict(signed)
        supplied = signed_payload.pop('signoffFingerprint')
        assert supplied == fingerprint(signed_payload)
        assert len(signed['evidence']) == len(PLAN['targets'])

        bad_path = root / 'firefox-desktop.json'
        bad = json.loads(bad_path.read_text(encoding='utf-8'))
        bad['rcIndexSha256'] = '0' * 64
        bad_payload = {key: value for key, value in bad.items() if key != 'evidenceFingerprint'}
        bad['evidenceFingerprint'] = fingerprint(bad_payload)
        bad_path.write_text(json.dumps(bad), encoding='utf-8')
        signoff.unlink()
        assert run(root, rc_status_path, signoff, report) == 2
        assert not signoff.exists()

        bad_path.write_text(json.dumps(fixture_payload(PLAN['targets'][0], rc_status)), encoding='utf-8')
        (root / 'firefox-copy.json').write_text(json.dumps(fixture_payload(PLAN['targets'][0], rc_status)), encoding='utf-8')
        assert run(root, rc_status_path) == 2

    print('V14_RC_ACCEPTANCE_SELF_TEST=PASS')
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence-dir')
    parser.add_argument('--rc-status', required=True)
    parser.add_argument('--write-signoff')
    parser.add_argument('--write-report')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        return self_test(args.rc_status)
    if not args.evidence_dir:
        parser.error('--evidence-dir is required unless --self-test is used')
    return run(args.evidence_dir, args.rc_status, args.write_signoff, args.write_report)


if __name__ == '__main__':
    raise SystemExit(main())
