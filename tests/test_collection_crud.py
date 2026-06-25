from pathlib import Path

from pydantic import BaseModel, EmailStr

from modelvault import Vault, model
from modelvault.errors import RecordNotFoundError, ValidationError


@model(key="id", storage="table", indexes=["email"])
class User(BaseModel):
    id: int
    email: EmailStr
    active: bool = True


def test_integration_flow(db_path: Path) -> None:
    vault = Vault.sqlite(db_path)
    users = vault.collection(User)

    users.insert(User(id=1, email="a@example.com"))
    assert users.get(1).email == "a@example.com"

    users.upsert(User(id=1, email="b@example.com"))
    assert users.get(1).email == "b@example.com"

    assert users.count() == 1
    assert users.find(email="b@example.com")[0].id == 1

    users.delete(1)
    assert users.count() == 0
    vault.close()


def test_exists_and_all(db_path: Path) -> None:
    vault = Vault.sqlite(db_path)
    users = vault.collection(User)
    users.insert(User(id=1, email="a@example.com"))
    users.insert(User(id=2, email="c@example.com"))
    assert users.exists(1)
    assert not users.exists(99)
    assert len(users.all()) == 2
    assert len(users.all(limit=1)) == 1
    vault.close()


def test_get_missing_raises(db_path: Path) -> None:
    vault = Vault.sqlite(db_path)
    users = vault.collection(User)
    try:
        users.get(999)
    except RecordNotFoundError:
        pass
    else:
        raise AssertionError("expected RecordNotFoundError")
    vault.close()


def test_invalid_write_fails(db_path: Path) -> None:
    vault = Vault.sqlite(db_path)
    users = vault.collection(User)
    try:
        users.insert({"id": 1, "email": "not-an-email"})
    except ValidationError:
        pass
    else:
        raise AssertionError("expected ValidationError")
    vault.close()
