"""Shared SQLAlchemy Core backend helpers."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine, Row, create_engine
from sqlalchemy.engine.interfaces import ReflectedColumn

from modelvault.errors import BackendError


class SQLAlchemyBackendBase:
    """Base implementation for SQLAlchemy Core backends."""

    def __init__(self, url: str, *, echo: bool = False) -> None:
        self._url = url
        self._engine: Engine = create_engine(url, echo=echo)

    @property
    def engine(self) -> Engine:
        return self._engine

    def execute(self, statement: Any, parameters: dict[str, Any] | None = None) -> Any:
        with self._engine.begin() as conn:
            return conn.execute(statement, parameters or {})

    def fetch_one(
        self, statement: Any, parameters: dict[str, Any] | None = None
    ) -> Row[Any] | None:
        with self._engine.connect() as conn:
            result = conn.execute(statement, parameters or {})
            return result.fetchone()

    def fetch_all(
        self, statement: Any, parameters: dict[str, Any] | None = None
    ) -> list[Row[Any]]:
        with self._engine.connect() as conn:
            result = conn.execute(statement, parameters or {})
            return list(result.fetchall())

    @contextmanager
    def begin(self) -> Iterator[Any]:
        with self._engine.begin() as conn:
            yield conn

    def close(self) -> None:
        self._engine.dispose()

    def health(self) -> dict[str, Any]:
        try:
            row = self.fetch_one(text("SELECT 1 AS ok"))
            ok = row is not None and row[0] == 1
            return {"ok": ok, "url": self._url}
        except Exception as exc:
            raise BackendError(f"Backend health check failed: {exc}") from exc

    def table_exists(self, name: str) -> bool:
        inspector = inspect(self._engine)
        return name in inspector.get_table_names()

    def reflect_columns(self, name: str) -> list[ReflectedColumn]:
        inspector = inspect(self._engine)
        return list(inspector.get_columns(name))
