"""Testes de integração da API (pytest + TestClient)."""
from __future__ import annotations


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_listar(client):
    r = client.get("/api/properties")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 15
    assert len(body["items"]) == 12  # per_page padrão
    assert body["page"] == 1
    assert body["pages"] == 2


def test_filtro_por_tipo(client):
    r = client.get("/api/properties", params={"tipo": "terreno", "per_page": 50})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 3
    assert all(it["tipo"] == "terreno" for it in body["items"])


def test_faixa_de_preco(client):
    r = client.get(
        "/api/properties",
        params={"preco_min": 300000, "preco_max": 700000, "per_page": 50},
    )
    assert r.status_code == 200
    for it in r.json()["items"]:
        assert 300000 <= float(it["preco"]) <= 700000


def test_quartos_min(client):
    r = client.get("/api/properties", params={"quartos_min": 4, "per_page": 50})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 1
    assert all(it["quartos"] >= 4 for it in body["items"])


def test_busca_textual(client):
    r = client.get("/api/properties", params={"q": "praia", "per_page": 50})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 1
    assert any("praia" in it["titulo"].lower() for it in body["items"])


def test_busca_textual_bairro(client):
    r = client.get("/api/properties", params={"q": "batel", "per_page": 50})
    assert r.status_code == 200
    assert any(it["bairro"].lower() == "batel" for it in r.json()["items"])


def test_ordenacao_preco_asc(client):
    r = client.get(
        "/api/properties", params={"ordenacao": "price_asc", "per_page": 50}
    )
    assert r.status_code == 200
    precos = [float(it["preco"]) for it in r.json()["items"]]
    assert precos == sorted(precos)


def test_ordenacao_area_desc(client):
    r = client.get(
        "/api/properties", params={"ordenacao": "area_desc", "per_page": 50}
    )
    assert r.status_code == 200
    areas = [it["area_m2"] for it in r.json()["items"]]
    assert areas == sorted(areas, reverse=True)


def test_ordenacao_invalida(client):
    r = client.get("/api/properties", params={"ordenacao": "xpto"})
    assert r.status_code == 422


def test_paginacao(client):
    r1 = client.get("/api/properties", params={"page": 1, "per_page": 5})
    r2 = client.get("/api/properties", params={"page": 2, "per_page": 5})
    b1, b2 = r1.json(), r2.json()
    assert b1["total"] == 15 and b1["pages"] == 3
    assert len(b1["items"]) == 5 and len(b2["items"]) == 5
    # Páginas diferentes não repetem itens.
    ids1 = {it["id"] for it in b1["items"]}
    ids2 = {it["id"] for it in b2["items"]}
    assert ids1.isdisjoint(ids2)


def test_detalhe_ok(client):
    r = client.get("/api/properties/1")
    assert r.status_code == 200
    assert r.json()["id"] == 1


def test_detalhe_404(client):
    r = client.get("/api/properties/99999")
    assert r.status_code == 404


def test_favoritar_201(client):
    r = client.post("/api/favorites", json={"property_id": 1})
    assert r.status_code == 201
    body = r.json()
    assert body["property_id"] == 1
    assert body["property"]["id"] == 1


def test_favoritar_inexistente_404(client):
    r = client.post("/api/favorites", json={"property_id": 99999})
    assert r.status_code == 404


def test_listar_e_remover_favorito(client):
    client.post("/api/favorites", json={"property_id": 2})
    client.post("/api/favorites", json={"property_id": 3})

    r = client.get("/api/favorites")
    assert r.status_code == 200
    ids = {it["property_id"] for it in r.json()}
    assert {2, 3} <= ids

    d = client.delete("/api/favorites/2")
    assert d.status_code == 204

    r2 = client.get("/api/favorites")
    ids2 = {it["property_id"] for it in r2.json()}
    assert 2 not in ids2 and 3 in ids2


def test_remover_favorito_inexistente_404(client):
    r = client.delete("/api/favorites/99999")
    assert r.status_code == 404
