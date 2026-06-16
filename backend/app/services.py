"""Camada de serviço — regras de negócio, validação e ordenação."""
from __future__ import annotations

import math
from decimal import Decimal
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .models import Favorite, Property
from .repositories import FavoriteRepository, PropertyRepository
from .schemas import PropertyPage

# Valores aceitos para a ordenação.
ORDENACOES_VALIDAS = {"price_asc", "price_desc", "area_desc"}

PER_PAGE_MAX = 50


class PropertyService:
    """Regras de negócio para imóveis."""

    def __init__(self, db: Session) -> None:
        self.repo = PropertyRepository(db)

    def search(
        self,
        *,
        tipo: Optional[str] = None,
        preco_min: Optional[Decimal] = None,
        preco_max: Optional[Decimal] = None,
        quartos_min: Optional[int] = None,
        cidade: Optional[str] = None,
        q: Optional[str] = None,
        ordenacao: Optional[str] = None,
        page: int = 1,
        per_page: int = 12,
    ) -> PropertyPage:
        # Validação/normalização dos parâmetros de controle.
        if ordenacao is not None and ordenacao not in ORDENACOES_VALIDAS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"ordenacao inválida: {ordenacao}",
            )
        page = max(1, page)
        per_page = max(1, min(per_page, PER_PAGE_MAX))

        items, total = self.repo.search(
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
        pages = math.ceil(total / per_page) if total else 0
        return PropertyPage(items=items, total=total, page=page, pages=pages)

    def get_or_404(self, property_id: int) -> Property:
        prop = self.repo.get(property_id)
        if prop is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Imóvel não encontrado",
            )
        return prop


class FavoriteService:
    """Regras de negócio para favoritos."""

    def __init__(self, db: Session) -> None:
        self.fav_repo = FavoriteRepository(db)
        self.prop_repo = PropertyRepository(db)

    def list_all(self) -> list[Favorite]:
        return self.fav_repo.list_all()

    def add(self, property_id: int) -> Favorite:
        # 404 se o imóvel não existir.
        if self.prop_repo.get(property_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Imóvel não encontrado",
            )
        # Idempotente: se já é favorito, devolve o existente.
        existente = self.fav_repo.get_by_property(property_id)
        if existente is not None:
            return existente
        return self.fav_repo.add(property_id)

    def remove(self, property_id: int) -> None:
        fav = self.fav_repo.get_by_property(property_id)
        if fav is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Favorito não encontrado",
            )
        self.fav_repo.remove(fav)
