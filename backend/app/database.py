"""Configuração do banco de dados (SQLAlchemy 2.x + SQLite)."""
from __future__ import annotations

import os
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# Caminho do arquivo SQLite ao lado do pacote (backend/app.db).
# Pode ser sobrescrito por DATABASE_URL (usado, por exemplo, nos testes).
_DEFAULT_DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app.db")
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{_DEFAULT_DB}")

# check_same_thread=False é necessário porque o SQLite, por padrão,
# amarra a conexão à thread que a criou — e o FastAPI usa várias threads.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Classe base declarativa para todos os modelos."""


def get_db() -> Iterator[Session]:
    """Dependência do FastAPI: entrega uma sessão e garante o fechamento."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
