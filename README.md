# Terrazo — Portal imobiliário (full-stack demo)

> ⚠️ **Aviso — código proprietário.** Este repositório é **somente para visualização** (demonstração de portfólio). **Proibido clonar, copiar, usar, modificar ou redistribuir**, no todo ou em parte, sem autorização por escrito. Todos os direitos reservados — ver [LICENSE](LICENSE).


Demonstração de um portal imobiliário completo: uma API REST profissional em
FastAPI servindo busca de imóveis com filtros, ordenação e paginação, mais um
sistema de favoritos — consumida por um frontend estático.

**🔗 Demo ao vivo:** https://devanshelltech.com.br/demos/imobiliaria/

## O que esta demo demonstra

- **Busca com filtros + paginação** (o destaque): filtragem por tipo, faixa de
  preço, número mínimo de quartos, cidade e busca textual em título/bairro,
  combinada com ordenação e paginação, retornando metadados de página
  (`total`, `page`, `pages`).
- Arquitetura em camadas bem separadas (router → service → repository).
- Tratamento correto de dinheiro com `Decimal`.
- Suíte de testes de integração cobrindo todos os fluxos.

## Arquitetura

API organizada em camadas, com responsabilidades isoladas:

```
backend/
  app/
    main.py            # app FastAPI, CORS, metadados e /docs
    database.py        # engine, sessão e Base (SQLAlchemy 2.x)
    models.py          # modelos ORM (Property, Favorite)
    schemas.py         # schemas Pydantic v2 (entrada/saída)
    repositories.py    # acesso a dados: busca, filtros e paginação
    services.py        # regras de negócio, validação e ordenação
    seed.py            # carga de ~15 imóveis de exemplo (idempotente)
    routers/
      properties.py    # rotas de imóveis
      favorites.py     # rotas de favoritos
  tests/               # pytest + TestClient
frontend/
  index.html           # interface estática
```

- **Router**: recebe a requisição e delega.
- **Service**: valida parâmetros (ex.: ordenação aceita), aplica regras e
  ordenação.
- **Repository**: monta a query de busca/filtros/paginação no banco.

## Como rodar

### Backend

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Popula o banco com imóveis de exemplo (idempotente)
.venv/bin/python -m app.seed

# Sobe a API
.venv/bin/uvicorn app.main:app --reload
```

- Documentação interativa: http://127.0.0.1:8000/docs
- Healthcheck: http://127.0.0.1:8000/api/health

### Testes

```bash
cd backend
.venv/bin/python -m pytest -q
```

### Frontend

Abra `frontend/index.html` no navegador (ou sirva a pasta com qualquer
servidor estático).

## Endpoints

| Método | Rota | Descrição |
| ------ | ---- | --------- |
| `GET` | `/api/health` | Healthcheck (`{"status":"ok"}`). |
| `GET` | `/api/properties` | Busca de imóveis. Filtros: `tipo`, `preco_min`, `preco_max`, `quartos_min`, `cidade`, `q`. Ordenação: `price_asc`, `price_desc`, `area_desc`. Paginação: `page`, `per_page`. Retorna `{items, total, page, pages}`. |
| `GET` | `/api/properties/{id}` | Detalhe do imóvel (404 se não existir). |
| `GET` | `/api/favorites` | Lista os favoritos. |
| `POST` | `/api/favorites` | Favorita um imóvel — corpo `{property_id}` (201; 404 se o imóvel não existir). |
| `DELETE` | `/api/favorites/{property_id}` | Remove o favorito. |

## Stack

- **Python**
- **FastAPI**
- **SQLAlchemy** (2.x)
- **SQLite**
- **Pydantic** (v2)
- **pytest**

---

© 2026 Wender Fernando Azevedo Falido · Devan Shell Tech — Todos os direitos
reservados. Código proprietário, ver LICENSE.
