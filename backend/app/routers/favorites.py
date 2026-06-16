"""Rotas de favoritos."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import FavoriteCreate, FavoriteOut
from ..services import FavoriteService

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


@router.get("", response_model=list[FavoriteOut], summary="Listar favoritos")
def list_favorites(db: Session = Depends(get_db)) -> list[FavoriteOut]:
    return FavoriteService(db).list_all()


@router.post(
    "",
    response_model=FavoriteOut,
    status_code=status.HTTP_201_CREATED,
    summary="Favoritar imóvel",
)
def create_favorite(
    payload: FavoriteCreate,
    db: Session = Depends(get_db),
) -> FavoriteOut:
    """Favorita um imóvel (404 se o imóvel não existir)."""
    return FavoriteService(db).add(payload.property_id)


@router.delete(
    "/{property_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover favorito",
)
def delete_favorite(
    property_id: int,
    db: Session = Depends(get_db),
) -> Response:
    """Remove um favorito pelo id do imóvel (404 se não for favorito)."""
    FavoriteService(db).remove(property_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
