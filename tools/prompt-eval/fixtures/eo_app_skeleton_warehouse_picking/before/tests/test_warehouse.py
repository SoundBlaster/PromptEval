from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from warehouse import commit_pick, plan_pick


INVENTORY = {
    "tea": [
        {"batch": "t1", "quantity": 2, "expires": 5},
        {"batch": "t2", "quantity": 3, "expires": 8},
    ],
    "mug": [
        {"batch": "m1", "quantity": 1, "expires": 30},
    ],
}


def test_plan_pick_uses_earliest_expiring_batches():
    order = [{"sku": "tea", "quantity": 4}, {"sku": "mug", "quantity": 1}]

    plan = plan_pick(INVENTORY, order)

    assert plan == {
        "picks": [
            {"sku": "tea", "batch": "t1", "quantity": 2},
            {"sku": "tea", "batch": "t2", "quantity": 2},
            {"sku": "mug", "batch": "m1", "quantity": 1},
        ],
        "shortages": [],
        "remaining": {"tea": {"t1": 0, "t2": 1}, "mug": {"m1": 0}},
    }


def test_plan_pick_shortage_uses_combined_demand_for_same_sku():
    order = [{"sku": "tea", "quantity": 2}, {"sku": "tea", "quantity": 4}]

    plan = plan_pick(INVENTORY, order)

    assert plan["picks"] == [
        {"sku": "tea", "batch": "t1", "quantity": 2},
        {"sku": "tea", "batch": "t2", "quantity": 3},
    ]
    assert plan["shortages"] == [{"sku": "tea", "quantity": 1}]
    assert plan["remaining"]["tea"] == {"t1": 0, "t2": 0}


def test_commit_pick_requires_carrier_acceptance_and_does_not_mutate_input():
    order = [{"sku": "tea", "quantity": 2}]

    rejected = commit_pick(INVENTORY, order, {"accepted": False})
    assert rejected == {
        "status": "rejected",
        "reason": "carrier_unavailable",
        "remaining": {"tea": {"t1": 2, "t2": 3}, "mug": {"m1": 1}},
    }

    committed = commit_pick(INVENTORY, order, {"accepted": True})
    assert committed == {
        "status": "committed",
        "picks": [{"sku": "tea", "batch": "t1", "quantity": 2}],
        "remaining": {"tea": {"t1": 0, "t2": 3}, "mug": {"m1": 1}},
    }
    assert INVENTORY["tea"][0]["quantity"] == 2
