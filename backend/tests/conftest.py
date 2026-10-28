import os, tempfile
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def client(monkeypatch, tmp_path):
    db=tmp_path/"test.db"
    monkeypatch.setenv("DATABASE_PATH", str(db))
    # The app config is imported before fixture execution, so initialize explicit test path
    import app.database.db as dbmod
    import app.main as mainmod
    monkeypatch.setattr(dbmod, "DATABASE_PATH", db)
    monkeypatch.setattr(mainmod, "connect", lambda path=None, readonly=False: dbmod.connect(path or db, readonly=readonly))
    monkeypatch.setattr(mainmod, "initialize", lambda: dbmod.initialize(db))
    monkeypatch.setattr(mainmod, "schema_info", lambda: dbmod.schema_info(db))
    dbmod.initialize(db)
    with TestClient(mainmod.app) as c: yield c
