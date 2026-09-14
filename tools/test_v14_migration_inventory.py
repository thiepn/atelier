from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from v14_migration_inventory import InventoryError, validate_inventory

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "src" / "v14" / "migration-inventory.json"


class MigrationInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads(INVENTORY.read_text(encoding="utf-8"))

    def test_repository_inventory_is_valid_stabilization(self):
        result = validate_inventory(copy.deepcopy(self.base))
        self.assertEqual(result["version"], "14.0.0-dev.14")
        self.assertEqual(result["phase"], "stabilization")
        self.assertFalse(result["selectionRequired"])
        self.assertIsNone(result["selected"])
        self.assertIn("dimension-formatting", result["completed"])
        self.assertEqual(result["currentCompleted"], [])
        self.assertEqual(len(result["frozenModules"]), 8)
        self.assertEqual(len(result["frozenPatches"]), 7)
        self.assertEqual(result["serviceWorker"]["mode"], "isolated-development")
        self.assertEqual(result["serviceWorker"]["cachePrefix"], "atelier-v14-dev-")
        self.assertTrue(result["serviceWorker"]["preserveBaselineCaches"])
        self.assertTrue(result["serviceWorker"]["precacheV14Assets"])
        self.assertGreaterEqual(result["blockedCount"], 4)

    def migration_copy(self):
        data = copy.deepcopy(self.base)
        data["policy"]["phase"] = "migration"
        data["policy"].pop("stabilization", None)
        return data

    def test_duplicate_boundary_is_rejected(self):
        data = copy.deepcopy(self.base)
        data["boundaries"].append(copy.deepcopy(data["boundaries"][0]))
        with self.assertRaises(InventoryError):
            validate_inventory(data)

    def test_stabilization_rejects_selected_next(self):
        data = copy.deepcopy(self.base)
        candidate = data["boundaries"][1]
        candidate.update({
            "decision": "selected-next",
            "targetMilestone": "14.0.0-dev.15",
            "stateRisk": "low",
            "mutationRisk": "none",
            "browserCoupling": "none",
            "testability": "high",
        })
        with self.assertRaises(InventoryError):
            validate_inventory(data)

    def test_stabilization_requires_architecture_freeze(self):
        data = copy.deepcopy(self.base)
        data["policy"]["stabilization"]["architectureFrozen"] = False
        with self.assertRaises(InventoryError):
            validate_inventory(data)

    def test_stabilization_blocks_new_legacy_bridges(self):
        data = copy.deepcopy(self.base)
        data["policy"]["stabilization"]["allowNewLegacyBridges"] = True
        with self.assertRaises(InventoryError):
            validate_inventory(data)

    def test_stabilization_requires_isolated_worker_mode(self):
        data = copy.deepcopy(self.base)
        data["policy"]["stabilization"]["serviceWorker"]["mode"] = "inherited"
        with self.assertRaises(InventoryError):
            validate_inventory(data)

    def test_stabilization_requires_baseline_cache_preservation(self):
        data = copy.deepcopy(self.base)
        data["policy"]["stabilization"]["serviceWorker"]["preserveBaselineCaches"] = False
        with self.assertRaises(InventoryError):
            validate_inventory(data)

    def test_stabilization_requires_v14_precache(self):
        data = copy.deepcopy(self.base)
        data["policy"]["stabilization"]["serviceWorker"]["precacheV14Assets"] = False
        with self.assertRaises(InventoryError):
            validate_inventory(data)

    def test_selection_required_needs_exactly_one_candidate(self):
        data = self.migration_copy()
        data["policy"]["selectionRequired"] = True
        with self.assertRaises(InventoryError):
            validate_inventory(data)

    def test_multiple_selected_boundaries_are_rejected(self):
        data = self.migration_copy()
        data["policy"]["selectionRequired"] = True
        completed = data["boundaries"][0]
        completed["decision"] = "hold"
        completed["targetMilestone"] = None
        for boundary in data["boundaries"][1:3]:
            boundary.update({
                "decision": "selected-next",
                "targetMilestone": "14.0.0-dev.15",
                "stateRisk": "low",
                "mutationRisk": "none",
                "browserCoupling": "none",
                "testability": "high",
            })
        with self.assertRaises(InventoryError):
            validate_inventory(data)

    def test_excluded_ownership_cannot_be_selected(self):
        data = self.migration_copy()
        data["policy"]["selectionRequired"] = True
        current = data["boundaries"][0]
        current["decision"] = "hold"
        current["targetMilestone"] = None
        blocked = next(b for b in data["boundaries"] if b["ownership"] == "project-persistence")
        blocked.update({
            "decision": "selected-next",
            "targetMilestone": "14.0.0-dev.15",
            "stateRisk": "low",
            "mutationRisk": "none",
            "browserCoupling": "none",
            "testability": "high",
        })
        with self.assertRaises(InventoryError):
            validate_inventory(data)

    def test_selected_boundary_must_be_non_mutating(self):
        data = self.migration_copy()
        data["policy"]["selectionRequired"] = True
        current = data["boundaries"][0]
        current["decision"] = "hold"
        current["targetMilestone"] = None
        candidate = data["boundaries"][1]
        candidate.update({
            "decision": "selected-next",
            "targetMilestone": "14.0.0-dev.15",
            "stateRisk": "low",
            "mutationRisk": "indirect",
            "browserCoupling": "none",
            "testability": "high",
        })
        with self.assertRaises(InventoryError):
            validate_inventory(data)

    def test_migration_closeout_requires_current_completed_boundary(self):
        data = self.migration_copy()
        data["policy"]["selectionRequired"] = False
        with self.assertRaises(InventoryError):
            validate_inventory(data)

    def test_completed_boundary_cannot_target_future_version(self):
        data = copy.deepcopy(self.base)
        data["boundaries"][0]["targetMilestone"] = "14.0.0-dev.99"
        with self.assertRaises(InventoryError):
            validate_inventory(data)

    def test_frozen_lists_must_be_unique(self):
        data = copy.deepcopy(self.base)
        data["policy"]["stabilization"]["frozenModules"].append(data["policy"]["stabilization"]["frozenModules"][0])
        with self.assertRaises(InventoryError):
            validate_inventory(data)


if __name__ == "__main__":
    unittest.main()
