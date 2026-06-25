from unittest.mock import MagicMock

from pydantic import BaseModel

from modelvault import model
from modelvault.contracts import build_contract
from modelvault.errors import PlanningError
from modelvault.planner import Planner


@model(key="id", storage="table")
class User(BaseModel):
    id: int
    email: str


def test_plan_insert_returns_insert_plan() -> None:
    planner = Planner()
    contract = build_contract(User)
    plan = planner.plan_insert(contract, {"id": 1, "email": "a@example.com"})
    assert plan.contract is contract
    assert plan.row["id"] == 1
    assert plan.schema_hash


def test_plan_read_returns_read_plan() -> None:
    planner = Planner()
    contract = build_contract(User)
    plan = planner.plan_read(contract, 1)
    assert plan.key == 1


def test_planning_has_no_database_side_effects() -> None:
    planner = Planner()
    contract = build_contract(User)
    backend = MagicMock()
    planner.plan_insert(contract, {"id": 1, "email": "x"})
    planner.plan_find(contract, {"email": "x"})
    backend.execute.assert_not_called()


def test_invalid_filters_fail() -> None:
    planner = Planner()
    contract = build_contract(User)
    try:
        planner.plan_find(contract, {"unknown": "x"})
    except PlanningError:
        pass
    else:
        raise AssertionError("expected PlanningError")
