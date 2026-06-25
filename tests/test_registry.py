from pathlib import Path

from pydantic import BaseModel

from modelvault import model
from modelvault.backends.sqlite import SQLiteBackend
from modelvault.contracts import build_contract
from modelvault.registry import Registry


@model(key="id", storage="table")
class User(BaseModel):
    id: int
    email: str


def test_metadata_tables_created(db_path: Path) -> None:
    backend = SQLiteBackend.from_path(db_path)
    registry = Registry(backend)
    registry.ensure_metadata()
    assert backend.table_exists("modelvault_registry")
    assert backend.table_exists("modelvault_schemas")
    backend.close()


def test_contract_stored_and_loaded(db_path: Path) -> None:
    backend = SQLiteBackend.from_path(db_path)
    registry = Registry(backend)
    contract = build_contract(User)
    registry.register_contract(contract)
    stored = registry.get_contract("users")
    assert stored is not None
    assert stored.model_name == "User"
    assert stored.key_field == "id"
    backend.close()


def test_list_contracts(db_path: Path) -> None:
    backend = SQLiteBackend.from_path(db_path)
    registry = Registry(backend)
    registry.register_contract(build_contract(User))
    contracts = registry.list_contracts()
    assert len(contracts) == 1
    backend.close()
