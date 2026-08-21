import pytest

from src import database


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    """Point the pipeline at a throwaway DuckDB file instead of the real one."""
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test_macro_analytics.duckdb")
    database.init_db()
