"""Popula o banco com imóveis de exemplo. Idempotente."""
from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select

from .database import Base, SessionLocal, engine
from .models import Property

# 15 imóveis variados (tipos, cidades, faixas de preço, nº de quartos).
IMOVEIS = [
    {"titulo": "Casa térrea com quintal", "tipo": "casa", "preco": Decimal("780000.00"), "quartos": 3, "area_m2": 180.0, "cidade": "Curitiba", "bairro": "Água Verde", "descricao": "Casa arejada com quintal amplo e churrasqueira."},
    {"titulo": "Apartamento alto padrão", "tipo": "apartamento", "preco": Decimal("1250000.00"), "quartos": 4, "area_m2": 145.0, "cidade": "Curitiba", "bairro": "Batel", "descricao": "Cobertura com vista panorâmica e duas vagas."},
    {"titulo": "Apartamento compacto", "tipo": "apartamento", "preco": Decimal("385000.00"), "quartos": 1, "area_m2": 42.0, "cidade": "Curitiba", "bairro": "Centro", "descricao": "Studio mobiliado próximo ao transporte público."},
    {"titulo": "Terreno em condomínio", "tipo": "terreno", "preco": Decimal("420000.00"), "quartos": 0, "area_m2": 360.0, "cidade": "Pinhais", "bairro": "Alphaville", "descricao": "Lote plano pronto para construir."},
    {"titulo": "Sala comercial mobiliada", "tipo": "comercial", "preco": Decimal("560000.00"), "quartos": 0, "area_m2": 70.0, "cidade": "São Paulo", "bairro": "Itaim Bibi", "descricao": "Sala comercial em prédio corporativo com recepção."},
    {"titulo": "Sobrado em rua tranquila", "tipo": "casa", "preco": Decimal("950000.00"), "quartos": 4, "area_m2": 220.0, "cidade": "São Paulo", "bairro": "Vila Mariana", "descricao": "Sobrado reformado com suíte master."},
    {"titulo": "Apartamento garden", "tipo": "apartamento", "preco": Decimal("690000.00"), "quartos": 2, "area_m2": 88.0, "cidade": "São Paulo", "bairro": "Pinheiros", "descricao": "Garden com área externa privativa e churrasqueira."},
    {"titulo": "Casa de praia", "tipo": "casa", "preco": Decimal("1100000.00"), "quartos": 5, "area_m2": 260.0, "cidade": "Florianópolis", "bairro": "Jurerê", "descricao": "Casa a poucos metros da praia com piscina."},
    {"titulo": "Apartamento frente mar", "tipo": "apartamento", "preco": Decimal("2300000.00"), "quartos": 3, "area_m2": 130.0, "cidade": "Florianópolis", "bairro": "Beira Mar Norte", "descricao": "Vista para o mar e infraestrutura completa de lazer."},
    {"titulo": "Terreno comercial de esquina", "tipo": "terreno", "preco": Decimal("880000.00"), "quartos": 0, "area_m2": 500.0, "cidade": "Florianópolis", "bairro": "Centro", "descricao": "Terreno de esquina com alto potencial construtivo."},
    {"titulo": "Loja em rua de grande fluxo", "tipo": "comercial", "preco": Decimal("740000.00"), "quartos": 0, "area_m2": 120.0, "cidade": "Curitiba", "bairro": "Rebouças", "descricao": "Ponto comercial consolidado com vitrine ampla."},
    {"titulo": "Casa de campo", "tipo": "casa", "preco": Decimal("640000.00"), "quartos": 3, "area_m2": 200.0, "cidade": "Campinas", "bairro": "Sousas", "descricao": "Casa em meio à natureza, ideal para descanso."},
    {"titulo": "Apartamento para investidor", "tipo": "apartamento", "preco": Decimal("315000.00"), "quartos": 2, "area_m2": 55.0, "cidade": "Campinas", "bairro": "Cambuí", "descricao": "Ótima rentabilidade para locação."},
    {"titulo": "Terreno residencial plano", "tipo": "terreno", "preco": Decimal("260000.00"), "quartos": 0, "area_m2": 250.0, "cidade": "Campinas", "bairro": "Barão Geraldo", "descricao": "Lote plano em bairro universitário valorizado."},
    {"titulo": "Conjunto de salas comerciais", "tipo": "comercial", "preco": Decimal("1450000.00"), "quartos": 0, "area_m2": 210.0, "cidade": "São Paulo", "bairro": "Faria Lima", "descricao": "Andar corporativo em região nobre de negócios."},
]


def seed() -> int:
    """Insere os imóveis se a tabela estiver vazia. Retorna quantos inseriu."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Idempotência: não duplica se já houver imóveis.
        if db.scalar(select(Property).limit(1)) is not None:
            return 0
        db.add_all(Property(**dados) for dados in IMOVEIS)
        db.commit()
        return len(IMOVEIS)
    finally:
        db.close()


if __name__ == "__main__":
    inseridos = seed()
    print(f"Seed concluído: {inseridos} imóveis inseridos.")
