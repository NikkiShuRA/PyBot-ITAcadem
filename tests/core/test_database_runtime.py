from __future__ import annotations

import pytest
from sqlalchemy import text

from pybot.db.database import create_database_engine


@pytest.mark.asyncio
async def test_create_database_engine_enables_sqlite_foreign_keys(tmp_path) -> None:
    database_url = f"sqlite+aiosqlite:///{(tmp_path / 'runtime_fk.sqlite3').as_posix()}"
    engine = create_database_engine(database_url)

    try:
        async with engine.connect() as connection:
            foreign_keys_enabled = await connection.scalar(text("PRAGMA foreign_keys"))
    finally:
        await engine.dispose()

    assert foreign_keys_enabled == 1
