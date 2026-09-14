#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import pathlib
import re
import tempfile
from urllib.parse import urlparse

HERE = pathlib.Path(__file__).resolve().parent
PLAN = json.loads((HERE / 'v14-rc-required-targets.json').read_text(encoding='utf-8'))
EXPECTED_PLAN_SCHEMA = 'atelier-v14-rc-acceptance-plan-v3'
ALLOWED_RESULT_STATUSES = {'NOT_TESTED', 'PASS', 'FAIL'}
VERSION_RE = re.compile(r'^14\.0\.0-dev\.\d+$')


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


def validate_plan():
    errors = []
    if PLAN.get('schema') != EXPECTED_PLAN_SCHEMA:
        errors.append(f'acceptance plan must use {EXPECTED_PLAN_SCHEMA}')
    deployment = PLAN.get('candidateDeployment')
    if not isinstance(deployment, dict):
        errors.append('candidateDeployment is required')
    else:
        for field in ('url', 'runnerUrl', 'statusUrl', 'productionUrl'):
            value = deployment.get(field)
            if not isinstance(value, str) or not value:
                errors.append(f'candidateDeployment.{field} is required')
        if deployment.get('httpsRequired') is not True:
            errors.append('candidateDeployment.httpsRequired must be true')
        if deployment.get('exactUrlEvidenceRequired') is not True:
            errors.append('candidateDeployment.exactUrlEvidenceRequired must be true')
        if deployment.get('versionedPathRequired') is not True:
            errors.append('candidateDeployment.versionedPathRequired must be true')
        if deployment.get('runnerCacheBustRequired') is not True:
            errors.append('candidateDeployment.runnerCacheBustRequired must be true')
    if errors:
        raise ValueError('; '.join(errors))


validate_plan()
DEPLOYMENT = PLAN['candidateDeployment']


def parse_url(value, *, require_directory=False, allow_query=False):
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = urlparse(value)
    except Exception:
        return None
    if parsed.scheme != 'https' or not parsed.netloc or parsed.username is not None or parsed.password is not None or parsed.fragment:
        return None
    if not allow_query and parsed.query:
        return None
    if require_directory and not parsed.path.endswith('/'):
        return None
    return parsed


def normalized_origin(value):
    parsed = parse_url(value, allow_query=True)
    if not parsed:
        return None
    return f'{parsed.scheme}://{parsed.netloc}/'


def expected_candidate_origin():
    return normalized_origin(DEPLOYMENT['url'])


def expected_rc_version():
    parsed = parse_url(DEPLOYMENT['url'], require_directory=True)
    if not parsed:
        raise ValueError('candidate deployment URL is invalid')
    versions = [part for part in parsed.path.split('/') if VERSION_RE.fullmatch(part)]
    if len(versions) != 1:
        raise ValueError('candidate deployment URL must contain exactly one V14 dev version')
    return versions[0]


EXPECTED_RC_VERSION = expected_rc_version()


def parse_timestamp(value):
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith('Z'):
        text = text[:-1] + '+00:00'
    try:
        parsed = datetime.datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed


def load_rc_status(path):
    status = json.loads(pathlib.Path(path).read_text(encoding='utf-8'))
    errors = []
    if not isinstance(status, dict):
        raise ValueError('RC status must be a JSON object')
    if status.get('schema') != PLAN['requiredRcStatusSchema']:
        errors.append('unexpected RC status schema')
    if status.get('artifactKind') != 'release-candidate':
        errors.append('artifactKind must be release-candidate')
    if status.get('diagnosticsStripped') is not True:
        errors.append('RC diagnostics are not marked stripped')
    if status.get('ownCacheLookupOnly') is not True:
        errors.append('RC status must declare own-cache-only service-worker reads')
    if status.get('productionEligible') is not False:
        errors.append('RC packaging must not claim final production eligibility')
    version = status.get('version')
    if not isinstance(version, str) or not VERSION_RE.fullmatch(version):
        errors.append('unexpected RC version')
    elif version != EXPECTED_RC_VERSION:
        errors.append(f'RC version does not match staged candidate path: expected {EXPECTED_RC_VERSION}, got {version}')
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
    else:
        if not isinstance(gate.get('priorReleaseGateReady'), bool):
            errors.append('certificationGate.priorReleaseGateReady must be boolean')
        if gate.get('promotionEligible') is not False:
            errors.append('certificationGate.promotionEligible must remain false before final cutover certification')
        blockers = gate.get('blockers')
        if not isinstance(blockers, list) or 'v14-physical-signoff-required' not in blockers or 'v14-cutover-verification-required' not in blockers:
            errors.append('certificationGate must retain V14 physical and cutover blockers')
    if errors:
        raise ValueError('; '.join(errors))
    return status


def prior_release_gate_ready(rc_status):
    return rc_status['certificationGate']['priorReleaseGateReady'] is True


def expected_identity(rc_status):
    return {
        'rcVersion': rc_status['version'],
        'rcIndexSha256': rc_status['indexSha256'],
        'rcServiceWorkerSha256': rc_status['serviceWorkerSha256'],
        'rcCache': rc_status['cache'],
        'candidateOrigin': expected_candidate_origin(),
        'candidateUrl': DEPLOYMENT['url'],
        'runnerUrl': DEPLOYMENT['runnerUrl'],
        'stagingStatusUrl': DEPLOYMENT['statusUrl'],
    }


def validate_file(path, rc_status):
    errors = []
    try:
        original = json.loads(pathlib.Path(path).read_text(encoding='utf-8'))
    except Exception as exc:
        return None, None, [f'invalid JSON: {exc}']
    if not isinstance(original, dict):
        return None, None, ['evidence must be a JSON object']

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

    candidate_url = original.get('candidateUrl')
    if parse_url(candidate_url, require_directory=True) is None:
        errors.append('candidateUrl must be a clean HTTPS directory URL')
    if candidate_url == DEPLOYMENT['productionUrl']:
        errors.append('candidateUrl must not be the production URL')
    if parse_url(original.get('runnerUrl'), allow_query=True) is None:
        errors.append('runnerUrl must be a valid HTTPS URL')
    if parse_url(original.get('stagingStatusUrl')) is None:
        errors.append('stagingStatusUrl must be a clean HTTPS URL')
    if original.get('candidateOrigin') != expected_candidate_origin():
        errors.append('candidateOrigin mismatch')

    if original.get('attested') is not True:
        errors.append('tester attestation missing')
    if not str(original.get('tester', '')).strip():
        errors.append('tester identity missing')
    for field in ('deviceModel', 'osVersion', 'browserVersion'):
        if not str(original.get(field, '')).strip():
            errors.append(f'{field} missing')

    environment = original.get('environment')
    if not isinstance(environment, dict):
        errors.append('environment must be an object')
    elif parse_timestamp(environment.get('timestamp')) is None:
        errors.append('environment.timestamp must be a timezone-aware ISO-8601 timestamp')

    target_data = original.get('target')
    target_id = target_data.get('id') if isinstance(target_data, dict) else None
    target = next((item for item in PLAN['targets'] if item['id'] == target_id), None)
    if not target:
        errors.append(f'unknown target {target_id!r}')
        return target_id, original, errors
    if target_data.get('label') != target['label']:
        errors.append('target label mismatch')

    results = original.get('results')
    result_map = {}
    seen_ids = []
    if not isinstance(results, list):
        errors.append('results must be a list')
    else:
        for result in results:
            if not isinstance(result, dict):
                errors.append('invalid result entry')
                continue
            result_id = result.get('id')
            if not isinstance(result_id, str) or not result_id:
                errors.append('result id is required')
                continue
            if result_id in result_map:
                errors.append(f'duplicate result {result_id!r}')
                continue
            status = result.get('status')
            if status not in ALLOWED_RESULT_STATUSES:
                errors.append(f'{result_id}: invalid status {status!r}')
            result_map[result_id] = status
            seen_ids.append(result_id)

    required_tests = target['requiredTests']
    required_set = set(required_tests)
    result_set = set(seen_ids)
    missing_results = sorted(required_set - result_set)
    extra_results = sorted(result_set - required_set)
    if missing_results:
        errors.append('missing result ids: ' + ', '.join(missing_results))
    if extra_results:
        errors.append('unexpected result ids: ' + ', '.join(extra_results))
    if len(seen_ids) != len(required_tests):
        errors.append(f'result count mismatch: expected {len(required_tests)}, got {len(seen_ids)}')
    for test_id in required_tests:
        if result_map.get(test_id) != 'PASS':
            errors.append(f'{test_id}: required PASS, got {result_map.get(test_id)!r}')
    return target_id, original, errors


def collect(evidence_dir, rc_status, exclude_paths=()):
    excluded = {pathlib.Path(path).resolve() for path in exclude_paths if path}
    files = [
        path for path in sorted(pathlib.Path(evidence_dir).glob('*.json'))
        if path.resolve() not in excluded
    ]
    by_target = {}
    failures = []
    for path in files:
        target_id, data, errors = validate_file(path, rc_status)
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
                    'candidateUrl': data.get('candidateUrl', ''),
                    'runnerUrl': data.get('runnerUrl', ''),
                    'stagingStatusUrl': data.get('stagingStatusUrl', ''),
                }
    required = {target['id'] for target in PLAN['targets']}
    missing = sorted(required - set(by_target))
    physical_ready = not failures and not missing
    return by_target, failures, missing, physical_ready


def build_physical_signoff(by_target, rc_status):
    target_order = [target['id'] for target in PLAN['targets']]
    prior_ready = prior_release_gate_ready(rc_status)
    payload = {
        'schema': PLAN['physicalSignoffSchema'],
        'acceptanceMilestone': PLAN['acceptanceMilestone'],
        **expected_identity(rc_status),
        'physicalState': 'PASS',
        'priorReleaseGateReady': prior_ready,
        'cutoverEligible': prior_ready,
        'productionPromotionReady': False,
        'requiredTargets': target_order,
        'evidence': [{'targetId': target_id, **by_target[target_id]} for target_id in target_order],
        'generatedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    output = dict(payload)
    output['signoffFingerprint'] = fingerprint(payload)
    return output


def build_report(by_target, failures, missing, physical_ready, rc_status):
    prior_ready = prior_release_gate_ready(rc_status)
    return {
        'acceptanceMilestone': PLAN['acceptanceMilestone'],
        **expected_identity(rc_status),
        'validEvidence': len(by_target),
        'requiredEvidence': len(PLAN['targets']),
        'failures': [{'filename': name, 'errors': errors} for name, errors in failures],
        'missing': missing,
        'physicalReady': physical_ready,
        'priorReleaseGateReady': prior_ready,
        'cutoverEligible': physical_ready and prior_ready,
        'productionPromotionReady': False,
        'priorReleaseBlockers': rc_status['certificationGate'].get('priorReleaseBlockers', []),
        'remainingPromotionBlockers': ['v14-cutover-verification-required'],
    }


def run(evidence_dir, rc_status_path, write_signoff=None, write_report=None):
    rc_status = load_rc_status(rc_status_path)
    excluded_outputs = [rc_status_path, write_signoff, write_report]
    by_target, failures, missing, physical_ready = collect(evidence_dir, rc_status, excluded_outputs)
    prior_ready = prior_release_gate_ready(rc_status)
    cutover_eligible = physical_ready and prior_ready
    print(f'VALID_RC_EVIDENCE={len(by_target)}/{len(PLAN["targets"])}')
    for target_id in sorted(by_target):
        print(f'PASS {target_id}: {by_target[target_id]["filename"]}')
    for name, errors in failures:
        for error in errors:
            print(f'FAIL {name}: {error}')
    for target_id in missing:
        print(f'PENDING {target_id}: evidence missing')
    print('PHYSICAL_READY=' + ('true' if physical_ready else 'false'))
    print('PRIOR_RELEASE_GATE_READY=' + ('true' if prior_ready else 'false'))
    print('CUTOVER_ELIGIBLE=' + ('true' if cutover_eligible else 'false'))
    print('PRODUCTION_PROMOTION_READY=false')
    if write_report:
        pathlib.Path(write_report).write_text(json.dumps(build_report(by_target, failures, missing, physical_ready, rc_status), indent=2) + '\n', encoding='utf-8')
    if write_signoff:
        if not physical_ready:
            print('PHYSICAL_SIGNOFF_FILE=not-written (physical gate blocked)')
        else:
            path = pathlib.Path(write_signoff)
            path.write_text(json.dumps(build_physical_signoff(by_target, rc_status), indent=2) + '\n', encoding='utf-8')
            print(f'PHYSICAL_SIGNOFF_FILE={path}')
    return 0 if physical_ready else 2


def fixture_payload(target, rc_status):
    payload = {
        'schema': PLAN['evidenceSchema'],
        'acceptanceMilestone': PLAN['acceptanceMilestone'],
        **expected_identity(rc_status),
        'target': {'id': target['id'], 'label': target['label']},
        'tester': 'CI fixture',
        'deviceModel': 'fixture',
        'osVersion': 'fixture',
        'browserVersion': 'fixture',
        'environment': {'timestamp': '2026-09-14T00:00:00+00:00'},
        'results': [{'id': test_id, 'status': 'PASS', 'notes': ''} for test_id in target['requiredTests']],
        'generalNotes': 'synthetic validator fixture',
        'attested': True,
    }
    output = dict(payload)
    output['evidenceFingerprint'] = fingerprint(payload)
    return output


def write_fixture(path, payload):
    path.write_text(json.dumps(payload, indent=2), encoding='utf-8')


def resign(payload):
    body = {key: value for key, value in payload.items() if key != 'evidenceFingerprint'}
    payload['evidenceFingerprint'] = fingerprint(body)
    return payload


def self_test(rc_status_path):
    rc_status = load_rc_status(rc_status_path)
    with tempfile.TemporaryDirectory() as temp_dir:
        root = pathlib.Path(temp_dir)
        targets = PLAN['targets']
        for target in targets:
            write_fixture(root / f'{target["id"]}.json', fixture_payload(target, rc_status))
        signoff = root / 'physical-signoff.json'
        report = root / 'report.json'
        assert run(root, rc_status_path, signoff, report) == 0
        report_data = json.loads(report.read_text(encoding='utf-8'))
        assert report_data['physicalReady'] is True
        assert report_data['candidateUrl'] == DEPLOYMENT['url']
        assert report_data['runnerUrl'] == DEPLOYMENT['runnerUrl']
        assert report_data['cutoverEligible'] is prior_release_gate_ready(rc_status)
        assert report_data['productionPromotionReady'] is False
        signed = json.loads(signoff.read_text(encoding='utf-8'))
        signed_payload = dict(signed)
        supplied = signed_payload.pop('signoffFingerprint')
        assert supplied == fingerprint(signed_payload)
        assert signed['productionPromotionReady'] is False
        assert len(signed['evidence']) == len(targets)

        # Idempotence: generated outputs may live alongside evidence without being re-ingested.
        assert run(root, rc_status_path, signoff, report) == 0
        rerun_report = json.loads(report.read_text(encoding='utf-8'))
        assert rerun_report['validEvidence'] == len(targets)
        assert rerun_report['failures'] == []

        firefox_path = root / 'firefox-desktop.json'
        good = fixture_payload(targets[0], rc_status)
        cases = []
        bad = json.loads(json.dumps(good)); bad['rcIndexSha256'] = '0' * 64; cases.append(bad)
        bad = json.loads(json.dumps(good)); bad['candidateUrl'] = DEPLOYMENT['productionUrl']; cases.append(bad)
        bad = json.loads(json.dumps(good)); bad['runnerUrl'] = DEPLOYMENT['runnerUrl'].replace('?v=' + EXPECTED_RC_VERSION, ''); cases.append(bad)
        bad = json.loads(json.dumps(good)); bad['target']['label'] = 'Wrong target'; cases.append(bad)
        bad = json.loads(json.dumps(good)); bad['results'].append({'id': 'unexpected-check', 'status': 'PASS', 'notes': ''}); cases.append(bad)
        bad = json.loads(json.dumps(good)); bad['environment']['timestamp'] = '2026-09-14T00:00:00'; cases.append(bad)
        for bad in cases:
            write_fixture(firefox_path, resign(bad))
            target_id, _, errors = validate_file(firefox_path, rc_status)
            assert target_id == 'firefox-desktop' and errors
        write_fixture(firefox_path, good)
        write_fixture(root / 'firefox-copy.json', fixture_payload(targets[0], rc_status))
        assert run(root, rc_status_path, signoff, report) == 2

        wrong_status = dict(rc_status)
        wrong_status['version'] = '14.0.0-dev.17'
        wrong_status['cache'] = 'atelier-v14-rc-14.0.0-dev.17'
        wrong_path = root / 'wrong-status.json'
        wrong_path.write_text(json.dumps(wrong_status), encoding='utf-8')
        try:
            load_rc_status(wrong_path)
        except ValueError:
            pass
        else:
            raise AssertionError('wrong candidate version status was accepted')

    print('V14_RC_ACCEPTANCE_SELF_TEST=PASS plan=v3 exact_url=true own_cache_only=true output_idempotent=true promotion_fail_closed=true')
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
