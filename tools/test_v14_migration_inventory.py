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

    def test_repository_inventory_is_valid(self):
        result = validate_inventory(copy.deepcopy(self.base))
        self.assertEqual(result["version"], "14.0.0-dev.11")
        self.assertEqual(result["selected"], "dimension-formatting")
        self.assertEqual(result["targetMilestone"], "14.0.0-dev.12")
        self.assertGreaterEqual(result["blockedCount"], 4)

    def test_duplicate_boundary_is_rejected(self):
        data = copy.deepcopy(self.base)
        data["boundaries"].append(copy.deepcopy(data["boundaries"][0]))
        with self.assertRaises(InventoryError):
            validate_inventory(data)

    def test_multiple_selected_boundaries_are_rejected(self):
        data = copy.deepcopy(self.base)
        second = data["boundaries"][1]
        second.update({
            "decision": "selected-next",
            "targetMilestone": "14.0.0-dev.12",
            "stateRisk": "low",
            "mutationRisk": "none",
            "browserCoupling": "none",
            "testability": "high",
        })
        with self.assertRaises(InventoryError):
            validate_inventory(data)

    def test_excluded_ownership_cannot_be_selected(self):
        data = copy.deepcopy(self.base)
        current = data["boundaries"][0]
        current["decision"] = "hold"
        current["targetMilestone"] = None
        blocked = next(b for b in data["boundaries"] if b["ownership"] == "project-persistence")
        blocked.update({
            "decision": "selected-next",
            "targetMilestone": "14.0.0-dev.12",
            "stateRisk": "low",
            "mutationRisk": "none",
            "browserCoupling": "none",
            "testability": "high",
        })
        with self.assertRaises(InventoryError):
            validate_inventory(data)

    def test_selected_boundary_must_be_non_mutating(self):
        data = copy.deepcopy(self.base)
        data["boundaries"][0]["mutationRisk"] = "indirect"
        with self.assertRaises(InventoryError):
            validate_inventory(data)


if __name__ == "__main__":
    unittest.main()
