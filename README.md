# Logos — Central de Resposta a Incidentes

MVP de gestão de incidentes para frota de 5.000 caminhões.  
**Demo:** https://logos-ixy9.onrender.com (cold start de 30–60 s no plano gratuito)  
**Vídeo:** [link]

---

## Setup local

### Backend

Requer Python 3.11+.

```bash
cd backend
python -m venv .venv
# Windows:
.\.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn api.main:app --reload
```

A API sobe em `http://localhost:8000`. O banco SQLite é criado e populado
com 100 incidentes de seed automaticamente no primeiro boot.  
Documentação interativa: `http://localhost:8000/docs`

### Frontend

Requer Node.js 18+.

```bash
cd frontend
npm ci
npm run dev
```

A interface sobe em `http://localhost:5173`.  
O proxy `/api → http://localhost:8000` está configurado no `vite.config.js`.

### Testes

```bash
cd backend
pytest -q          # esperado: 9 passed
```

Checagem de tipos do frontend:

```bash
cd frontend
npx tsc --noEmit
```

---

## Decisões de arquitetura

### Concorrência otimista com `version`

Cada incidente tem um campo `version`. PATCH e DELETE exigem
`expected_version` no corpo; se o valor não bater com o banco, o servidor
devolve 409 com o estado atual em `error.current`.

A alternativa (lock pessimista) prenderia o incidente se o analista fechasse
a aba sem concluir a ação. Concorrência otimista reduz a janela de conflito e
não deixa registros presos.

### Regra `not_assignee` (403)

Assumir um incidente grava `assigned_to`. A partir daí, só o responsável pode
fechar, marcar inconclusivo ou devolver à fila. Sem essa regra, o `version`
protegeria apenas o instante do claim: dois analistas poderiam trabalhar em
paralelo no mesmo incidente.

### Máquina de estados no servidor

`allowed_transitions` vem da resposta da API. O frontend não duplica a lógica:
renderiza os botões que o servidor autoriza. Isso garante que a regra vive em
um único lugar e pode ser testada independentemente da interface.

### Deploy em serviço único (Render)

O Dockerfile usa build multi-stage: estágio Node gera o `dist` do frontend;
estágio Python copia o `dist` para dentro do FastAPI, que o serve como
arquivos estáticos. Sem CORS em produção, sem infraestrutura extra.

O banco SQLite usa modo WAL para reduzir contenção em leituras concorrentes.
O disco no Render é efêmero: o seed recria os 100 incidentes a cada boot.

### Polling em vez de WebSocket

`refetchInterval: 10_000` no TanStack Query atualiza a lista a cada 10 s.
WebSocket adicionaria complexidade de infraestrutura sem ganho prático para
100 incidentes. O `refetchOnWindowFocus` reduz a janela de dados obsoletos
quando o analista volta à aba.

### Fechados ocultos por padrão

Sem filtro de status, a API exclui incidentes Fechados. O analista vê apenas
o que requer ação. `status=Fechado` os mostra explicitamente.

---

## Limitações declaradas

| Limitação | Motivo |
|---|---|
| Sem autenticação | `X-Analyst` identifica o analista mas não autentica. Declarado no enunciado como fora do escopo. |
| Banco efêmero | Render gratuito não tem disco persistente. Em produção, trocar por PostgreSQL. |
| Formulário de criação cortado | POST disponível via `/docs` (Swagger). Declarado no escopo do MVP. |
| Sem paginação | 100 incidentes cabem em uma resposta. Adicionaria complexidade sem benefício no contexto do case. |

---

## Uso de IA

Claude Code foi utilizado como ferramenta de apoio ao desenvolvimento do projeto. Todo o código gerado ou sugerido pela ferramenta foi revisado e validado, incluindo sua integração com o backend real.


## Estrutura do repositório

```
logos/
├── backend/
│   ├── api/
│   │   ├── main.py          # app FastAPI, seed, static files
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── errors.py        # exception handlers
│   │   ├── routers/
│   │   └── services/
│   └── tests/
│       ├── conftest.py
│       └── test_incidents.py
├── frontend/
│   └── src/
│       ├── api/             # client, types, endpoints
│       ├── hooks/           # useIncidents, useUpdateIncident, ...
│       ├── components/      # Header, IncidentList, IncidentDrawer, ...
│       └── styles/
├── Dockerfile
└── docker-compose.yml
```