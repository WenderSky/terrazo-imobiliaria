"""Fixtures de teste — banco SQLite isolado em arquivo temporário."""
from __future__ import annotations

import os
import tempfile

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import Property  # noqa: F401  (garante o mapeamento)
from app.seed import IMOVEIS


@pytest.fixture()
def client():
    """TestClient com banco próprio e dados de seed carregados."""
    # Banco temporário por teste, descartado no fim.
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    engine = create_engine(
        f"sqlite:///{path}", connect_args={"check_same_thread": False}
    )
    TestingSession = sessionmaker(
        bind=engine, autoflush=False, expire_on_commit=False
    )

    Base.metadata.create_all(bind=engine)

    # Carrega os imóveis de exemplo.
    db = TestingSession()
    db.add_all(Property(**dados) for dados in IMOVEIS)
    db.commit()
    db.close()

    # Sobrescreve a dependência para usar o banco de teste.
    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    from fastapi.testclient import TestClient

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    engine.dispose()
    os.remove(path)
