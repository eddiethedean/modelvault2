from pathlib import Path

from sqlalchemy import text

from modelvault.backends.sqlite import SQLiteBackend


def test_engine_creates(db_path: Path) -> None:
    backend = SQLiteBackend.from_path(db_path)
    assert backend.engine is not None
    backend.close()


def test_health_passes(db_path: Path) -> None:
    backend = SQLiteBackend.from_path(db_path)
    health = backend.health()
    assert health["ok"] is True
    backend.close()


def test_execute_and_fetch(db_path: Path) -> None:
    backend = SQLiteBackend.from_path(db_path)
    backend.execute(text("CREATE TABLE t (id INTEGER PRIMARY KEY, name TEXT)"))
    with backend.begin() as conn:
        conn.execute(text("INSERT INTO t (id, name) VALUES (1, 'a')"))
    row = backend.fetch_one(text("SELECT name FROM t WHERE id = 1"))
    assert row is not None
    assert row[0] == "a"
    backend.close()


def test_table_exists(db_path: Path) -> None:
    backend = SQLiteBackend.from_path(db_path)
    backend.execute(text("CREATE TABLE items (id INTEGER PRIMARY KEY)"))
    assert backend.table_exists("items")
    assert not backend.table_exists("missing")
    backend.close()
