from pathlib import Path

from pydantic import BaseModel, EmailStr
from sqlalchemy import text

from modelvault import Vault, model
from modelvault.errors import DriftError


@model(key="id", storage="table")
class User(BaseModel):
    id: int
    email: EmailStr


def test_validate_all_reports_invalid_rows(db_path: Path) -> None:
    vault = Vault.sqlite(db_path)
    users = vault.collection(User)
    users.insert(User(id=1, email="ok@example.com"))
    with vault._backend.begin() as conn:  # noqa: SLF001
        conn.execute(text("UPDATE users SET email = 'not-an-email' WHERE id = 1"))
    report = users.validate_all()
    assert report.invalid_count >= 1
    vault.close()


def test_drift_on_model_change(db_path: Path) -> None:
    vault = Vault.sqlite(db_path)
    vault.collection(User)
    vault.close()

    @model(key="id", storage="table", table_name="users")
    class UserV2(BaseModel):
        id: int
        email: EmailStr
        active: bool = True

    vault2 = Vault.sqlite(db_path)
    try:
        vault2.collection(UserV2)
    except DriftError:
        pass
    else:
        raise AssertionError("expected DriftError")
    vault2.close()
