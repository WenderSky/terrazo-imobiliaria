"""Modelos ORM (SQLAlchemy 2.x, estilo mapped_column)."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Property(Base):
    """Imóvel anunciado no portal."""

    __tablename__ = "properties"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(160), index=True)
    # tipo: casa | apartamento | terreno | comercial
    tipo: Mapped[str] = mapped_column(String(20), index=True)
    # Dinheiro sempre em Decimal — Numeric preserva a precisão.
    preco: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    quartos: Mapped[int] = mapped_column(default=0)
    area_m2: Mapped[float] = mapped_column()
    cidade: Mapped[str] = mapped_column(String(80), index=True)
    bairro: Mapped[str] = mapped_column(String(80), index=True)
    descricao: Mapped[str] = mapped_column(String(2000), default="")
    imagem_url: Mapped[str] = mapped_column(String(500), default="")

    favorites: Mapped[list[Favorite]] = relationship(
        back_populates="property",
        cascade="all, delete-orphan",
    )


class Favorite(Base):
    """Marcação de um imóvel como favorito."""

    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(primary_key=True)
    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    property: Mapped[Property] = relationship(back_populates="favorites")
