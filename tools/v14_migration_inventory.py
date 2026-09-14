#!/usr/bin/env python3
"""Validate the V14 migration/dependency inventory and migration-selection policy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

SCHEMA = "atelier-v14-migration-inventory-v1"
ALLOWED_STATE_RISK = {"low", "medium", "high", "critical"}
ALLOWED_MUTATION_RISK = {"none", "indirect", "direct"}
ALLOWED_CALL_SURFACE = {"localized", "broad-readonly", "broad"}
ALLOWED_BROWSER_COUPLING = {"none", "low", "medium", "high"}
ALLOWED_TESTABILITY = {"low", "medium", "high"}
ALLOWED_PAYOFF = {"low", "medium", "high"}
ALLOWED_DECISION = {"selected-next", "completed", "hold", "defer", "blocked"}
BROWSER_ORDER = {"none": 0, "low": 1, "medium": 2, "high": 3}


class InventoryError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise InventoryError(message)


def validate_inventory(data: dict) -> dict:
    require(data.get("schema") == SCHEMA, f"schema must be {SCHEMA}")
    version = data.get("version")
    require(isinstance(version, str) and version.startswith("14.0.0-dev."), "invalid inventory version")

    policy = data.get("policy")
    require(isinstance(policy, dict), "policy must be an object")
    excluded = policy.get("excludedByDefault")
    require(isinstance(excluded, list) and excluded, "excludedByDefault must be a non-empty list")
    require(len(excluded) == len(set(excluded)), "excludedByDefault contains duplicates")
    require(all(isinstance(x, str) and x for x in excluded), "excludedByDefault entries must be strings")
    selection_required = policy.get("selectionRequired", True)
    require(isinstance(selection_required, bool), "selectionRequired must be boolean")

    rules = policy.get("selectionRules")
    require(isinstance(rules, dict), "selectionRules must be an object")
    require(rules.get("requiredStateRisk") in ALLOWED_STATE_RISK, "invalid requiredStateRisk")
    require(rules.get("requiredTestability") in ALLOWED_TESTABILITY, "invalid requiredTestability")
    require(rules.get("maxBrowserCoupling") in ALLOWED_BROWSER_COUPLING, "invalid maxBrowserCoupling")
    require(rules.get("requiresLegacyFallback") is True, "V14 selection must require legacy fallback")

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
            require(isinstance(target, str) and target, f"{boundary_id}: selected boundary requires targetMilestone")
        elif decision == "completed":
            completed.append(boundary)
            require(isinstance(target, str) and target, f"{boundary_id}: completed boundary requires targetMilestone")
            require(target <= version, f"{boundary_id}: completed targetMilestone cannot be newer than inventory version")
        else:
            require(target is None, f"{boundary_id}: only selected-next/completed may set targetMilestone")

    if selection_required:
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

    current_completed = [b for b in completed if b["targetMilestone"] == version]
    if not selection_required:
        require(current_completed, "selectionRequired=false requires a completed migration at the current inventory version")

    return {
        "version": version,
        "selectionRequired": selection_required,
        "selected": chosen["id"] if chosen else None,
        "targetMilestone": chosen["targetMilestone"] if chosen else None,
        "completed": [b["id"] for b in completed],
        "currentCompleted": [b["id"] for b in current_completed],
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
        f"selection_required={str(result['selectionRequired']).lower()} "
        f"selected={result['selected'] or 'none'} "
        f"completed={','.join(result['completed']) or 'none'} "
        f"boundaries={result['boundaryCount']} "
        f"blocked={result['blockedCount']} "
        f"deferred={result['deferredCount']}"
    )


if __name__ == "__main__":
    main()
