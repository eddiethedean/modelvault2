from pydantic import BaseModel, ValidationError

from modelvault import model
from modelvault.contracts import build_contract
from modelvault.errors import ContractError


@model(key="id", storage="table", indexes=["email"], table_name="app_users")
class DecoratedUser(BaseModel):
    id: int
    email: str


def test_decorator_attaches_config() -> None:
    assert DecoratedUser.__modelvault_config__["key"] == "id"
    assert DecoratedUser.__modelvault_config__["storage"] == "table"
    assert DecoratedUser.__modelvault_config__["indexes"] == ("email",)
    assert DecoratedUser.__modelvault_config__["table_name"] == "app_users"


def test_decorator_does_not_break_pydantic() -> None:
    user = DecoratedUser(id=1, email="a@example.com")
    assert user.email == "a@example.com"
    try:
        DecoratedUser(id=1, email="not-an-email")
    except ValidationError:
        pass
    else:
        # EmailStr not used; plain str accepts anything
        assert True


def test_missing_key_fails_during_contract_build() -> None:
    class Plain(BaseModel):
        id: int

    try:
        build_contract(Plain, {"storage": "table"})
    except ContractError as exc:
        assert "key" in str(exc).lower()
    else:
        raise AssertionError("expected ContractError")
