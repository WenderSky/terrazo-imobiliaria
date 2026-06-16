"""Camada de acesso a dados — toda query (busca/filtros/paginação) vive aqui."""
from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.orm import Session

from .models import Favorite, Property

# Mapeamento de chave de ordenação -> coluna/direção SQLAlchemy.
_ORDER_CLAUSES = {
    "price_asc": asc(Property.preco),
    "price_desc": desc(Property.preco),
    "area_desc": desc(Property.area_m2),
}


class PropertyRepository:
    """Consultas à tabela de imóveis."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, property_id: int) -> Optional[Property]:
        return self.db.get(Property, property_id)

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
    ) -> tuple[list[Property], int]:
        """Aplica filtros, ordenação e paginação. Retorna (itens, total)."""
        stmt = select(Property)

        if tipo:
            stmt = stmt.where(Property.tipo == tipo)
        if preco_min is not None:
            stmt = stmt.where(Property.preco >= preco_min)
        if preco_max is not None:
            stmt = stmt.where(Property.preco <= preco_max)
        if quartos_min is not None:
            stmt = stmt.where(Property.quartos >= quartos_min)
        if cidade:
            stmt = stmt.where(func.lower(Property.cidade) == cidade.lower())
        if q:
            # Busca textual (case-insensitive) em título e bairro.
            termo = f"%{q.lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(Property.titulo).like(termo),
                    func.lower(Property.bairro).like(termo),
                )
            )

        # Total antes de paginar (subconsulta sobre os filtros já aplicados).
        total = self.db.scalar(
            select(func.count()).select_from(stmt.subquery())
        )

        # Ordenação: a chave já chega validada pelo service.
        if ordenacao in _ORDER_CLAUSES:
            stmt = stmt.order_by(_ORDER_CLAUSES[ordenacao])
        else:
            stmt = stmt.order_by(asc(Property.id))

        stmt = stmt.limit(per_page).offset((page - 1) * per_page)
        items = list(self.db.scalars(stmt).all())
        return items, int(total or 0)


class FavoriteRepository:
    """Consultas à tabela de favoritos."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_property(self, property_id: int) -> Optional[Favorite]:
        stmt = select(Favorite).where(Favorite.property_id == property_id)
        return self.db.scalar(stmt)

    def list_all(self) -> list[Favorite]:
        stmt = select(Favorite).order_by(desc(Favorite.criado_em))
        return list(self.db.scalars(stmt).all())

    def add(self, property_id: int) -> Favorite:
        fav = Favorite(property_id=property_id)
        self.db.add(fav)
        self.db.commit()
        self.db.refresh(fav)
        return fav

    def remove(self, fav: Favorite) -> None:
        self.db.delete(fav)
        self.db.commit()
