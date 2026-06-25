from pathlib import Path

from pydantic import BaseModel

from modelvault import model
from modelvault.backends.sqlite import SQLiteBackend
from modelvault.contracts import build_contract
from modelvault.planner import Planner
from modelvault.storage.table import TableStorage


@model(key="id", storage="table", indexes=["email"])
class User(BaseModel):
    id: int
    email: str
    tags: list[str] = []


def test_table_created(db_path: Path) -> None:
    backend = SQLiteBackend.from_path(db_path)
    contract = build_contract(User)
    TableStorage().ensure_schema(contract, backend)
    assert backend.table_exists("users")
    backend.close()


def test_insert_and_get(db_path: Path) -> None:
    backend = SQLiteBackend.from_path(db_path)
    storage = TableStorage()
    contract = build_contract(User)
    storage.ensure_schema(contract, backend)
    planner = Planner()
    plan = planner.plan_insert(
        contract,
        {"id": 1, "email": "a@example.com", "tags": '["x"]'},
    )
    storage.insert(plan, backend)
    row = storage.get(planner.plan_read(contract, 1), backend)
    assert row["email"] == "a@example.com"
    backend.close()


def test_index_created(db_path: Path) -> None:
    backend = SQLiteBackend.from_path(db_path)
    contract = build_contract(User)
    TableStorage().ensure_schema(contract, backend)
    row = backend.fetch_one(
        __import__("sqlalchemy", fromlist=["text"]).text(
            "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'ix_users_%'"
        )
    )
    assert row is not None
    backend.close()
