# Commit Places — MVP estilo Airbnb

Projeto do Capítulo 2 (backend em Django REST) e Capítulo 3 (frontend em HTML, CSS e JS puro).

Anfitriões cadastram imóveis; hóspedes pesquisam, informam as datas de entrada e saída
e solicitam a reserva; o anfitrião aprova ou recusa cada pedido.

```
airbnb_clone/
├── backend/          API em Django REST Framework
│   ├── core/         configurações e rotas principais
│   ├── users/        cadastro, login por token e papéis
│   └── listings/     imóveis, fotos e reservas
├── frontend/         HTML + CSS + JavaScript
└── docker-compose.yml
```

---

## Como rodar

### Opção 1 — Docker (PostgreSQL, tudo pronto)

```bash
docker compose up --build
```

Sobe três serviços: banco PostgreSQL, API em `http://localhost:8000` e frontend em
`http://localhost:5500`. As migrações e os dados de exemplo são aplicados sozinhos.

### Contas de exemplo

| Usuário     | Senha      | Papel     |
|-------------|------------|-----------|
| `anfitriao` | `senha123` | Anfitrião |
| `hospede`   | `senha123` | Hóspede   |

---

## Documentação da API

Base: `http://localhost:8000/api`

Autenticação por **token**. Depois do login, envie o cabeçalho em toda requisição protegida:

```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

### Autenticação

| Método | Rota               | Acesso   | Descrição |
|--------|--------------------|----------|-----------|
| POST   | `/auth/register/`  | Público  | Cria conta e devolve o token |
| POST   | `/auth/login/`     | Público  | Devolve o token |
| GET    | `/auth/me/`        | Logado   | Dados do usuário logado |

**POST `/auth/register/`**

```json
{
  "username": "maria",
  "email": "maria@exemplo.com",
  "first_name": "Maria",
  "password": "senha123",
  "is_host": false
}
```

Resposta `201`:

```json
{
  "token": "9944b0919...",
  "user": { "id": 3, "username": "maria", "email": "maria@exemplo.com",
            "first_name": "Maria", "is_host": false }
}
```

**POST `/auth/login/`** — `{"username": "maria", "password": "senha123"}` →
mesma resposta acima. Credenciais erradas devolvem `400`.

---

### Imóveis — `/properties/`

| Método | Rota                    | Acesso            | Descrição |
|--------|-------------------------|-------------------|-----------|
| GET    | `/properties/`          | Público           | Lista com busca e filtros |
| GET    | `/properties/{id}/`     | Público           | Detalhe + datas ocupadas |
| GET    | `/properties/mine/`     | Anfitrião logado  | Só os imóveis dele |
| POST   | `/properties/`          | Anfitrião         | Cadastra imóvel |
| PATCH  | `/properties/{id}/`     | Dono do imóvel    | Atualiza |
| DELETE | `/properties/{id}/`     | Dono do imóvel    | Remove |

**Filtros da barra de pesquisa** (parâmetros de query, todos opcionais e combináveis):

| Parâmetro    | Exemplo      | Efeito |
|--------------|--------------|--------|
| `city`       | `Rio`        | Cidade contendo o texto |
| `min_price`  | `150`        | Diária a partir de |
| `max_price`  | `600`        | Diária até |
| `check_in`   | `2026-08-01` | Usado junto com `check_out` |
| `check_out`  | `2026-08-05` | Esconde imóveis com reserva aprovada no período |

```
GET /api/properties/?city=Rio&min_price=100&max_price=500
    &check_in=2026-08-01&check_out=2026-08-05
```

Resposta (lista de objetos como este):

```json
{
  "id": 1,
  "host": { "id": 1, "username": "anfitriao", "first_name": "Ana", "is_host": true },
  "title": "Loft moderno em Copacabana",
  "description": "A duas quadras da praia...",
  "address": "Rua Barata Ribeiro, 200",
  "city": "Rio de Janeiro",
  "price_per_night": "320.00",
  "max_guests": 4,
  "amenities": ["Wi-Fi", "Ar-condicionado", "Cozinha", "TV"],
  "rating": 4.8,
  "images": [{ "id": 1, "property": 1, "url": "https://..." }],
  "booked_dates": ["2026-08-01", "2026-08-02"],
  "created_at": "2026-07-30T12:00:00Z"
}
```

`booked_dates` lista os dias já ocupados por reservas **aprovadas**
(o dia do check-out fica livre para uma nova entrada).

**POST `/properties/`** — o campo `host` é ignorado se enviado; a API sempre usa o
usuário do token.

```json
{
  "title": "Chalé na serra",
  "description": "Com lareira",
  "address": "Estrada da Independência, 45",
  "city": "Petrópolis",
  "price_per_night": 410,
  "max_guests": 5,
  "amenities": ["Wi-Fi", "Lareira"]
}
```

---

### Fotos — `/property-images/`

| Método | Rota                        | Acesso         |
|--------|-----------------------------|----------------|
| POST   | `/property-images/`         | Dono do imóvel |
| DELETE | `/property-images/{id}/`    | Dono do imóvel |

```json
{ "property": 1, "url": "https://images.unsplash.com/photo-..." }
```

---

### Reservas — `/reservations/`

| Método | Rota                           | Acesso            | Descrição |
|--------|--------------------------------|-------------------|-----------|
| GET    | `/reservations/`               | Logado            | Hóspede vê as suas; anfitrião vê as recebidas |
| POST   | `/reservations/`               | Hóspede           | Solicita reserva (status `PENDING`) |
| POST   | `/reservations/{id}/approve/`  | Anfitrião do imóvel | Aprova |
| POST   | `/reservations/{id}/reject/`   | Anfitrião do imóvel | Recusa |

**POST `/reservations/`**

```json
{ "property": 1, "check_in": "2026-08-10", "check_out": "2026-08-14", "guests_count": 2 }
```

Validações aplicadas: saída depois da entrada, entrada não pode ser no passado,
número de hóspedes dentro da capacidade, período sem conflito com outra reserva
aprovada e o anfitrião não pode reservar o próprio imóvel.

Resposta `201`:

```json
{
  "id": 7,
  "property": 1,
  "property_detail": { "...": "objeto completo do imóvel" },
  "guest": { "id": 2, "username": "hospede", "first_name": "Bruno", "is_host": false },
  "check_in": "2026-08-10",
  "check_out": "2026-08-14",
  "guests_count": 2,
  "nights": 4,
  "total_price": "1280.00",
  "status": "PENDING",
  "status_display": "Pendente",
  "created_at": "2026-07-30T12:00:00Z"
}
```

Status possíveis: `PENDING` (Pendente), `APPROVED` (Aprovada), `REJECTED` (Recusada).
O status não pode ser alterado por `PATCH` — só pelas ações `approve` / `reject`,
e apenas enquanto estiver `PENDING`.

---

### Erros

| Código | Quando |
|--------|--------|
| `400`  | Dados inválidos — corpo com `{"campo": ["mensagem"]}` |
| `401`  | Token ausente ou inválido |
| `403`  | Sem permissão (ex.: responder reserva de outro anfitrião) |
| `404`  | Não existe ou não pertence a você |

---

## Telas do frontend

| Arquivo          | Função |
|------------------|--------|
| `index.html`     | Home: destaques e barra de busca com filtros |
| `imovel.html`    | Detalhe do imóvel e pedido de reserva |
| `login.html`     | Entrar e criar conta (hóspede ou anfitrião) |
| `reservas.html`  | Painel do hóspede: status das solicitações |
| `painel.html`    | Painel do anfitrião: aprova/recusa pedidos e gerencia imóveis |