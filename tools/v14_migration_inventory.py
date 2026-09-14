#!/usr/bin/env python3
"""Validate the V14 migration/dependency inventory and stabilization policy."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

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
        f"boundaries={result['boundaryCount']} "
        f"blocked={result['blockedCount']} "
        f"deferred={result['deferredCount']}"
    )


if __name__ == "__main__":
    main()
