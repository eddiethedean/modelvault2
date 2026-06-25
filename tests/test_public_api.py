from pathlib import Path

from pydantic import BaseModel, EmailStr

from modelvault import Vault, model


@model(key="id", storage="table")
class User(BaseModel):
    id: int
    email: EmailStr
    active: bool = True


def test_public_imports() -> None:
    from modelvault import ModelVaultError, Vault, model

    assert Vault is not None
    assert model is not None
    assert ModelVaultError is not None


def test_readme_example(db_path: Path) -> None:
    vault = Vault.sqlite(db_path)
    users = vault.collection(User)

    users.insert(User(id=1, email="alice@example.com"))
    loaded = users.get(1)

    assert isinstance(loaded, User)
    assert loaded.email == "alice@example.com"
    vault.close()
