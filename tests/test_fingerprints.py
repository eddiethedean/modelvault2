from pydantic import BaseModel

from modelvault import model
from modelvault.contracts import build_contract
from modelvault.fingerprint import fingerprint_contract


@model(key="id", storage="table", indexes=["email"])
class User(BaseModel):
    id: int
    email: str


def test_same_model_same_hash() -> None:
    c1 = build_contract(User)
    c2 = build_contract(User)
    assert fingerprint_contract(c1) == fingerprint_contract(c2)


def test_field_addition_changes_hash() -> None:
    base = fingerprint_contract(build_contract(User))

    @model(key="id", storage="table")
    class UserV2(BaseModel):
        id: int
        email: str
        active: bool = True

    assert fingerprint_contract(build_contract(UserV2)) != base


def test_key_change_changes_hash() -> None:
    base = fingerprint_contract(build_contract(User))

    @model(key="user_id", storage="table")
    class Other(BaseModel):
        user_id: int
        email: str

    assert fingerprint_contract(build_contract(Other)) != base


def test_index_change_changes_hash() -> None:
    base = fingerprint_contract(build_contract(User))

    @model(key="id", storage="table", indexes=["id"])
    class Indexed(BaseModel):
        id: int
        email: str

    assert fingerprint_contract(build_contract(Indexed)) != base


def test_ordering_is_deterministic() -> None:
    hashes = {fingerprint_contract(build_contract(User)) for _ in range(5)}
    assert len(hashes) == 1
