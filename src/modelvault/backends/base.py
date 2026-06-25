"""Backend protocol."""

from __future__ import annotations

from contextlib import AbstractContextManager
from typing import Any, Protocol

from sqlalchemy.engine import Row


class Backend(Protocol):
    def execute(self, statement: Any, parameters: dict[str, Any] | None = None) -> Any: ...

    def fetch_one(
        self, statement: Any, parameters: dict[str, Any] | None = None
    ) -> Row[Any] | None: ...

    def fetch_all(
        self, statement: Any, parameters: dict[str, Any] | None = None
    ) -> list[Row[Any]]: ...

    def begin(self) -> AbstractContextManager[Any]: ...

    def close(self) -> None: ...

    def health(self) -> dict[str, Any]: ...

    def table_exists(self, name: str) -> bool: ...
