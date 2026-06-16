"""Schemas Pydantic v2 (entrada/saída da API)."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PropertyOut(BaseModel):
    """Representação de um imóvel na resposta."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    tipo: str
    preco: Decimal
    quartos: int
    area_m2: float
    cidade: str
    bairro: str
    descricao: str
    imagem_url: str


class PropertyPage(BaseModel):
    """Página de resultados da busca de imóveis."""

    items: list[PropertyOut]
    total: int
    page: int
    pages: int


class FavoriteCreate(BaseModel):
    """Corpo para favoritar um imóvel."""

    property_id: int = Field(..., ge=1)


class FavoriteOut(BaseModel):
    """Favorito retornado pela API, com o imóvel embutido."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    property_id: int
    criado_em: datetime
    property: PropertyOut


class HealthOut(BaseModel):
    """Resposta do healthcheck."""

    status: str
