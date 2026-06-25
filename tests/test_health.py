from pathlib import Path

from pydantic import BaseModel, EmailStr

from modelvault import Vault, model


@model(key="id", storage="table")
class User(BaseModel):
    id: int
    email: EmailStr
    active: bool = True


def test_healthy_vault(db_path: Path) -> None:
    vault = Vault.sqlite(db_path)
    vault.collection(User)
    users = vault.collection(User)
    users.insert(User(id=1, email="alice@example.com"))
    health = vault.health()
    assert health.backend_ok
    assert health.metadata_ok
    assert health.healthy
    vault.close()


def test_describe_collection(db_path: Path) -> None:
    vault = Vault.sqlite(db_path)
    users = vault.collection(User)
    users.insert(User(id=1, email="alice@example.com"))
    desc = vault.describe(User)
    assert desc.collection_name == "users"
    assert desc.record_count == 1
    assert not desc.drift_detected
    vault.close()
