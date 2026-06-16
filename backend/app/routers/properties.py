"""Rotas de imóveis."""
from __future__ import annotations

from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import PropertyOut, PropertyPage
from ..services import PropertyService

router = APIRouter(prefix="/api/properties", tags=["properties"])


@router.get("", response_model=PropertyPage, summary="Buscar imóveis")
def list_properties(
    tipo: Optional[str] = Query(None, description="casa|apartamento|terreno|comercial"),
    preco_min: Optional[Decimal] = Query(None, ge=0),
    preco_max: Optional[Decimal] = Query(None, ge=0),
    quartos_min: Optional[int] = Query(None, ge=0),
    cidade: Optional[str] = Query(None),
    q: Optional[str] = Query(None, description="Busca em título e bairro"),
    ordenacao: Optional[str] = Query(
        None, description="price_asc|price_desc|area_desc"
    ),
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1),
    db: Session = Depends(get_db),
) -> PropertyPage:
    """Lista imóveis com filtros, ordenação e paginação."""
    return PropertyService(db).search(
        tipo=tipo,
        preco_min=preco_min,
        preco_max=preco_max,
        quartos_min=quartos_min,
        cidade=cidade,
        q=q,
        ordenacao=ordenacao,
        page=page,
        per_page=per_page,
    )


@router.get("/{property_id}", response_model=PropertyOut, summary="Detalhe do imóvel")
def get_property(
    property_id: int,
    db: Session = Depends(get_db),
) -> PropertyOut:
    """Retorna um imóvel pelo id (404 se não existir)."""
    return PropertyService(db).get_or_404(property_id)
