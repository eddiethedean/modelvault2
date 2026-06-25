from pathlib import Path

from pydantic import BaseModel

from modelvault import Vault, model
from modelvault.backends.sqlite import SQLiteBackend
from modelvault.contracts import build_contract
from modelvault.errors import DriftError
from modelvault.registry import Registry


@model(key="id", storage="table")
class User(BaseModel):
    id: int
    email: str


def test_drift_detected(db_path: Path) -> None:
    backend = SQLiteBackend.from_path(db_path)
    registry = Registry(backend)
    contract = build_contract(User)
    registry.register_contract(contract)

    @model(key="id", storage="table", table_name="users")
    class UserV2(BaseModel):
        id: int
        email: str
        active: bool = True

    new_contract = build_contract(UserV2)
    report = registry.detect_drift(new_contract)
    assert report is not None
    assert report.status == "drift_detected"
    backend.close()


def test_register_raises_on_drift(db_path: Path) -> None:
    vault = Vault.sqlite(db_path)
    vault.collection(User)

    @model(key="id", storage="table", table_name="users")
    class UserV2(BaseModel):
        id: int
        email: str
        active: bool = True

    try:
        vault.collection(UserV2)
    except DriftError as exc:
        assert exc.details is not None
    else:
        raise AssertionError("expected DriftError")
    vault.close()
