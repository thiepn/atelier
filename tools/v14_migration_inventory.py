#!/usr/bin/env python3
"""Validate the V14 migration/dependency inventory and stabilization policy."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

SCHEMA = "atelier-v14-migration-inventory-v1"
ALLOWED_PHASE = {"migration", "stabilization"}
ALLOWED_STATE_RISK = {"low", "medium", "high", "critical"}
ALLOWED_MUTATION_RISK = {"none", "indirect", "direct"}
ALLOWED_CALL_SURFACE = {"localized", "broad-readonly", "broad"}
ALLOWED_BROWSER_COUPLING = {"none", "low", "medium", "high"}
ALLOWED_TESTABILITY = {"low", "medium", "high"}
ALLOWED_PAYOFF = {"low", "medium", "high"}
ALLOWED_DECISION = {"selected-next", "completed", "hold", "defer", "blocked"}
BROWSER_ORDER = {"none": 0, "low": 1, "medium": 2, "high": 3}
VERSION_RE = re.compile(r"^14\.0\.0-dev\.(\d+)$")
PRODUCTION_URL = "https://thiepn.github.io/atelier/"
STAGING_BASE = "v14-rc-staging/"


class InventoryError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise InventoryError(message)


def version_number(value: str, field: str) -> int:
    match = VERSION_RE.fullmatch(value or "")
    require(match is not None, f"invalid {field}: {value!r}")
    return int(match.group(1))


def unique_string_list(value, field: str) -> list[str]:
    require(isinstance(value, list) and value, f"{field} must be a non-empty list")
    require(all(isinstance(x, str) and x for x in value), f"{field} entries must be strings")
    require(len(value) == len(set(value)), f"{field} contains duplicates")
    return value


def https_url(value: str, field: str, *, allow_query: bool = False) -> object:
    require(isinstance(value, str) and value, f"{field} is required")
    parsed = urlparse(value)
    require(parsed.scheme == "https" and bool(parsed.netloc), f"{field} must use HTTPS")
    require(parsed.username is None and parsed.password is None, f"{field} must not include credentials")
    require(not parsed.fragment, f"{field} must not include a fragment")
    require(allow_query or not parsed.query, f"{field} must not include a query")
    return parsed


def validate_inventory(data: dict) -> dict:
    require(data.get("schema") == SCHEMA, f"schema must be {SCHEMA}")
    version = data.get("version")
    current_version_number = version_number(version, "inventory version")

    policy = data.get("policy")
    require(isinstance(policy, dict), "policy must be an object")
    phase = policy.get("phase", "migration")
    require(phase in ALLOWED_PHASE, f"invalid policy phase: {phase}")

    excluded = unique_string_list(policy.get("excludedByDefault"), "excludedByDefault")
    selection_required = policy.get("selectionRequired", True)
    require(isinstance(selection_required, bool), "selectionRequired must be boolean")

    rules = policy.get("selectionRules")
    require(isinstance(rules, dict), "selectionRules must be an object")
    require(rules.get("requiredStateRisk") in ALLOWED_STATE_RISK, "invalid requiredStateRisk")
    require(rules.get("requiredTestability") in ALLOWED_TESTABILITY, "invalid requiredTestability")
    require(rules.get("maxBrowserCoupling") in ALLOWED_BROWSER_COUPLING, "invalid maxBrowserCoupling")
    require(rules.get("requiresLegacyFallback") is True, "V14 selection must require legacy fallback")

    stabilization = policy.get("stabilization")
    frozen_modules: list[str] = []
    frozen_patches: list[str] = []
    worker_policy: dict | None = None
    rc_policy: dict | None = None
    staging_policy: dict | None = None
    if phase == "stabilization":
        require(selection_required is False, "stabilization phase requires selectionRequired=false")
        require(isinstance(stabilization, dict), "stabilization policy is required")
        require(stabilization.get("architectureFrozen") is True, "stabilization requires architectureFrozen=true")
        require(stabilization.get("allowNewLegacyBridges") is False, "stabilization must block new legacy bridges")
        require(stabilization.get("allowProductionCutover") is False, "stabilization cannot authorize production cutover")
        frozen_modules = unique_string_list(stabilization.get("frozenModules"), "stabilization.frozenModules")
        frozen_patches = unique_string_list(stabilization.get("frozenPatches"), "stabilization.frozenPatches")

        worker_policy = stabilization.get("serviceWorker")
        require(isinstance(worker_policy, dict), "stabilization.serviceWorker policy is required")
        require(worker_policy.get("mode") == "isolated-development", "stabilization worker mode must be isolated-development")
        require(worker_policy.get("cachePrefix") == "atelier-v14-dev-", "unexpected stabilization worker cachePrefix")
        require(worker_policy.get("preserveBaselineCaches") is True, "stabilization worker must preserve baseline caches")
        require(worker_policy.get("precacheV14Assets") is True, "stabilization worker must precache V14 assets")
        require(worker_policy.get("ownCacheLookupOnly") is True, "stabilization worker must use own-cache-only reads")
        require(worker_policy.get("crossNamespaceReadsForbidden") is True, "stabilization worker must forbid cross-namespace reads")

        rc_policy = stabilization.get("releaseCandidatePackaging")
        require(isinstance(rc_policy, dict), "stabilization.releaseCandidatePackaging policy is required")
        require(rc_policy.get("enabled") is True, "release-candidate packaging must be enabled")
        require(rc_policy.get("stripDevelopmentDiagnostics") is True, "release-candidate packaging must strip development diagnostics")
        require(rc_policy.get("cachePrefix") == "atelier-v14-rc-", "unexpected release-candidate cachePrefix")
        require(rc_policy.get("cachePrefix") != worker_policy.get("cachePrefix"), "release-candidate cachePrefix must differ from development cachePrefix")
        require(rc_policy.get("certificationMatrix") == "CERTIFICATION_MATRIX_13.3.1.json", "release-candidate packaging must bind the 13.3.1 certification matrix")
        require(rc_policy.get("requirePriorSignoffBeforePromotion") is True, "release-candidate promotion must require prior signoff")
        require(rc_policy.get("physicalAcceptancePlan") == "acceptance/v14-rc-required-targets.json", "unexpected RC physical acceptance plan")
        require(rc_policy.get("physicalAcceptanceValidator") == "acceptance/validate_v14_rc_acceptance.py", "unexpected RC physical acceptance validator")
        require(rc_policy.get("cutoverPlan") == "acceptance/v14-rc-cutover-plan.json", "unexpected RC cutover plan")
        require(rc_policy.get("allowPhysicalEvidenceBeforePriorSignoff") is True, "RC physical evidence must be collectable before prior signoff")
        require(rc_policy.get("allowPromotionBeforePriorSignoff") is False, "RC promotion must remain blocked before prior signoff")

        staging_policy = stabilization.get("staging")
        require(isinstance(staging_policy, dict), "stabilization.staging policy is required")
        require(staging_policy.get("enabled") is True, "staging must be enabled")
        require(staging_policy.get("publishBranch") == "main", "staging publishBranch must be main")
        require(staging_policy.get("publishBasePath") == STAGING_BASE, "unexpected staging publishBasePath")
        require(staging_policy.get("versionedCandidatePath") is True, "staging must use a versioned candidate path")
        require(staging_policy.get("preservePriorCandidates") is True, "staging must preserve prior candidates")
        expected_path = f"{STAGING_BASE}{version}/"
        require(staging_policy.get("candidatePath") == expected_path, "staging candidatePath must exactly match the inventory version")
        require(staging_policy.get("productionUrl") == PRODUCTION_URL, "unexpected staging production URL")
        require(staging_policy.get("productionRootRuntimeImmutable") is True, "staging must preserve the production root runtime")
        require(staging_policy.get("serviceWorkerScopeIsolatedByPath") is True, "staging worker scope must be isolated by path")
        require(staging_policy.get("parentProductionWorkerMayControlFirstNavigation") is True, "staging must model parent-worker first-navigation control")
        require(staging_policy.get("runnerCacheBustRequired") is True, "staging runner cache bust is required")
        require(staging_policy.get("liveHttpsVerificationRequired") is True, "staging live HTTPS verification is required")
        require(staging_policy.get("physicalEvidenceRunner") == "acceptance.html", "unexpected staging evidence runner")

        candidate_url = staging_policy.get("candidateUrl")
        runner_url = staging_policy.get("runnerUrl")
        status_url = staging_policy.get("statusUrl")
        candidate_parsed = https_url(candidate_url, "staging.candidateUrl")
        runner_parsed = https_url(runner_url, "staging.runnerUrl", allow_query=True)
        status_parsed = https_url(status_url, "staging.statusUrl")
        expected_web_path = f"/atelier/{expected_path}"
        require(candidate_parsed.path == expected_web_path + "app/", "staging candidateUrl path must match candidatePath/app/")
        require(runner_parsed.path == expected_web_path + "acceptance.html", "staging runnerUrl path must match candidatePath/acceptance.html")
        query = parse_qs(runner_parsed.query)
        require(query.get("v") == [version], "staging runnerUrl must include exactly v=<version>")
        require(status_parsed.path == expected_web_path + "staging-status.json", "staging statusUrl path must match candidatePath/staging-status.json")
        require(candidate_parsed.netloc == runner_parsed.netloc == status_parsed.netloc, "staging URLs must share one host")
        require(candidate_url != PRODUCTION_URL, "staging candidate URL must differ from production")
    else:
        require(stabilization is None, "migration phase must not carry a stabilization freeze")

    boundaries = data.get("boundaries")
    require(isinstance(boundaries, list) and boundaries, "boundaries must be a non-empty list")

    ids: set[str] = set()
    selected: list[dict] = []
    completed: list[dict] = []
    for index, boundary in enumerate(boundaries):
        prefix = f"boundaries[{index}]"
        require(isinstance(boundary, dict), f"{prefix} must be an object")
        boundary_id = boundary.get("id")
        require(isinstance(boundary_id, str) and boundary_id, f"{prefix}.id is required")
        require(boundary_id not in ids, f"duplicate boundary id: {boundary_id}")
        ids.add(boundary_id)

        symbols = boundary.get("symbols")
        require(isinstance(symbols, list) and symbols and all(isinstance(x, str) and x for x in symbols), f"{boundary_id}: symbols must be a non-empty string list")
        require(isinstance(boundary.get("legacyArea"), str) and boundary["legacyArea"], f"{boundary_id}: legacyArea is required")
        ownership = boundary.get("ownership")
        require(isinstance(ownership, str) and ownership, f"{boundary_id}: ownership is required")
        require(boundary.get("stateRisk") in ALLOWED_STATE_RISK, f"{boundary_id}: invalid stateRisk")
        require(boundary.get("mutationRisk") in ALLOWED_MUTATION_RISK, f"{boundary_id}: invalid mutationRisk")
        require(boundary.get("callSurface") in ALLOWED_CALL_SURFACE, f"{boundary_id}: invalid callSurface")
        require(boundary.get("browserCoupling") in ALLOWED_BROWSER_COUPLING, f"{boundary_id}: invalid browserCoupling")
        require(boundary.get("testability") in ALLOWED_TESTABILITY, f"{boundary_id}: invalid testability")
        require(boundary.get("userPayoff") in ALLOWED_PAYOFF, f"{boundary_id}: invalid userPayoff")
        decision = boundary.get("decision")
        require(decision in ALLOWED_DECISION, f"{boundary_id}: invalid decision")
        require(isinstance(boundary.get("rationale"), str) and boundary["rationale"].strip(), f"{boundary_id}: rationale is required")

        if ownership in excluded:
            require(decision == "blocked", f"{boundary_id}: excluded ownership {ownership} must be blocked")

        target = boundary.get("targetMilestone")
        if decision == "selected-next":
            selected.append(boundary)
            version_number(target, f"{boundary_id}.targetMilestone")
        elif decision == "completed":
            completed.append(boundary)
            target_number = version_number(target, f"{boundary_id}.targetMilestone")
            require(target_number <= current_version_number, f"{boundary_id}: completed targetMilestone cannot be newer than inventory version")
        else:
            require(target is None, f"{boundary_id}: only selected-next/completed may set targetMilestone")

    if phase == "stabilization":
        require(len(selected) == 0, f"stabilization requires zero selected-next boundaries, found {len(selected)}")
        require(completed, "stabilization requires at least one completed migration")
    elif selection_required:
        require(len(selected) == 1, f"exactly one selected-next boundary required, found {len(selected)}")
    else:
        require(len(selected) == 0, f"selectionRequired=false requires zero selected-next boundaries, found {len(selected)}")
        require(completed, "selectionRequired=false requires at least one completed migration")

    chosen = selected[0] if selected else None
    if chosen:
        require(chosen["stateRisk"] == rules["requiredStateRisk"], "selected boundary violates requiredStateRisk")
        require(chosen["testability"] == rules["requiredTestability"], "selected boundary violates requiredTestability")
        require(BROWSER_ORDER[chosen["browserCoupling"]] <= BROWSER_ORDER[rules["maxBrowserCoupling"]], "selected boundary exceeds browser coupling limit")
        require(chosen["mutationRisk"] == "none", "selected boundary must not mutate application state")
        require(chosen["ownership"] not in excluded, "selected boundary uses excluded ownership")

    current_completed = [b for b in completed if version_number(b["targetMilestone"], f"{b['id']}.targetMilestone") == current_version_number]
    if phase == "migration" and not selection_required:
        require(current_completed, "migration phase with selectionRequired=false requires a completed migration at the current inventory version")
    if phase == "stabilization":
        require(not current_completed, "stabilization milestone must not claim a new legacy migration")

    return {
        "version": version,
        "phase": phase,
        "selectionRequired": selection_required,
        "selected": chosen["id"] if chosen else None,
        "targetMilestone": chosen["targetMilestone"] if chosen else None,
        "completed": [b["id"] for b in completed],
        "currentCompleted": [b["id"] for b in current_completed],
        "frozenModules": frozen_modules,
        "frozenPatches": frozen_patches,
        "serviceWorker": worker_policy,
        "releaseCandidatePackaging": rc_policy,
        "staging": staging_policy,
        "boundaryCount": len(boundaries),
        "blockedCount": sum(1 for b in boundaries if b["decision"] == "blocked"),
        "deferredCount": sum(1 for b in boundaries if b["decision"] in {"defer", "hold"}),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", type=Path, default=Path("src/v14/migration-inventory.json"))
    args = parser.parse_args()

    data = json.loads(args.inventory.read_text(encoding="utf-8"))
    try:
        result = validate_inventory(data)
    except InventoryError as exc:
        print(f"V14_MIGRATION_INVENTORY_OK=false error={exc}")
        raise SystemExit(1)

    rc = result["releaseCandidatePackaging"] or {}
    staging = result["staging"] or {}
    print(
        "V14_MIGRATION_INVENTORY_OK=true "
        f"version={result['version']} "
        f"phase={result['phase']} "
        f"selection_required={str(result['selectionRequired']).lower()} "
        f"selected={result['selected'] or 'none'} "
        f"completed={','.join(result['completed']) or 'none'} "
        f"frozen_modules={len(result['frozenModules'])} "
        f"frozen_patches={len(result['frozenPatches'])} "
        f"worker_mode={(result['serviceWorker'] or {}).get('mode', 'none')} "
        f"own_cache_only={str((result['serviceWorker'] or {}).get('ownCacheLookupOnly', False)).lower()} "
        f"rc_packaging={str(rc.get('enabled', False)).lower()} "
        f"staging_versioned={str(staging.get('versionedCandidatePath', False)).lower()} "
        f"boundaries={result['boundaryCount']} "
        f"blocked={result['blockedCount']} "
        f"deferred={result['deferredCount']}"
    )


if __name__ == "__main__":
    main()
