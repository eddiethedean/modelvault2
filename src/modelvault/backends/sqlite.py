"""SQLite backend via SQLAlchemy Core."""

from __future__ import annotations

from pathlib import Path

from modelvault.backends.sqlalchemy import SQLAlchemyBackendBase


class SQLiteBackend(SQLAlchemyBackendBase):
    """SQLite database backend."""

    @classmethod
    def from_path(cls, path: str | Path, *, echo: bool = False) -> SQLiteBackend:
        resolved = Path(path).resolve()
        url = f"sqlite:///{resolved}"
        return cls(url, echo=echo)
