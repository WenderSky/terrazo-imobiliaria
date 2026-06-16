"""Aplicação FastAPI do portal imobiliário Terrazo."""
from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import favorites, properties
from .schemas import HealthOut

# Metadados das tags exibidas no /docs.
TAGS_METADATA = [
    {"name": "properties", "description": "Busca, filtros e detalhe de imóveis."},
    {"name": "favorites", "description": "Gerenciamento de imóveis favoritos."},
    {"name": "health", "description": "Verificação de disponibilidade."},
]

@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Cria as tabelas no boot (suficiente para uma demo sem migrações)."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Terrazo API",
    description="Portal imobiliário — busca, filtros, paginação e favoritos.",
    version="1.0.0",
    openapi_tags=TAGS_METADATA,
    lifespan=lifespan,
)

# CORS liberado para o frontend estático consumir a API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthOut, tags=["health"])
def health() -> HealthOut:
    return HealthOut(status="ok")


app.include_router(properties.router)
app.include_router(favorites.router)
