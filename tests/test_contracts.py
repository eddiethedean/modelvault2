from pydantic import BaseModel

from modelvault import model
from modelvault.contracts import build_contract
from modelvault.errors import ContractError


@model(key="id", storage="table", indexes=["email"])
class User(BaseModel):
    id: int
    email: str


def test_contract_builds_from_decorated_model() -> None:
    contract = build_contract(User)
    assert contract.model_name == "User"
    assert contract.key.field == "id"
    assert contract.table_name == "users"
    assert contract.storage.mode == "table"


def test_contract_builds_from_manual_registration() -> None:
    class Item(BaseModel):
        id: int
        name: str

    contract = build_contract(Item, {"key": "id", "storage": "table"})
    assert contract.collection_name == "items"


def test_key_must_exist() -> None:
    class NoKey(BaseModel):
        name: str

    try:
        build_contract(NoKey, {"key": "id", "storage": "table"})
    except ContractError:
        pass
    else:
        raise AssertionError("expected ContractError")


def test_indexes_must_exist() -> None:
    try:
        build_contract(User, {"key": "id", "storage": "table", "indexes": ["missing"]})
    except ContractError:
        pass
    else:
        raise AssertionError("expected ContractError")


def test_unsupported_storage_fails() -> None:
    try:
        build_contract(User, {"key": "id", "storage": "hybrid"})
    except ContractError:
        pass
    else:
        raise AssertionError("expected ContractError")


def test_non_pydantic_fails() -> None:
    try:
        build_contract(str)  # type: ignore[arg-type]
    except ContractError:
        pass
    else:
        raise AssertionError("expected ContractError")
