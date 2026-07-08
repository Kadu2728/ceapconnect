# Deploy — CEAP Connect

Guia de publicação em produção.

- **Frontend (Next.js)** → **Vercel**
- **Backend (FastAPI)** → **Render** (Docker, via [`render.yaml`](./render.yaml))
- **Banco (PostgreSQL)** → **Neon** (gerenciado, já provisionado)

A ordem importa: o backend precisa existir primeiro para o frontend saber a
URL da API, e o backend precisa do domínio do frontend para liberar o CORS.

---

## Pré-requisitos

- Repositório no GitHub (frontend + backend no mesmo repo — monorepo).
- Connection string **assíncrona** do Neon, no formato:
  `postgresql+asyncpg://<user>:<password>@<host>/<db>`
  (sem `?sslmode=...&channel_binding=...` na URL — o TLS é ativado via
  `DATABASE_SSL=true`).

---

## 1. Push para o GitHub

```bash
git remote add origin https://github.com/<usuario>/ceap-connect.git
git push -u origin main
```

---

## 2. Backend no Render

1. Render → **New +** → **Blueprint** → conecte o repositório.
2. O Render detecta o [`render.yaml`](./render.yaml) e cria o serviço
   `ceap-connect-api` (Docker, plano free).
3. Preencha as variáveis marcadas como segredo:
   - `DATABASE_URL` → connection string assíncrona do Neon.
   - `CORS_ORIGINS` → deixe temporariamente `https://localhost:3000`; será
     atualizado no passo 4 com o domínio real da Vercel.
   - `JWT_SECRET` é gerado automaticamente pelo Render.
4. Deploy. O container roda `alembic upgrade head` no boot (migrations
   automáticas) e sobe o Uvicorn.
5. Valide: `https://ceap-connect-api.onrender.com/api/v1/health` deve
   retornar `{"success":true,...,"database":"up"}`.

> **Cold start:** no plano free o serviço hiberna após ~15 min de
> inatividade; a primeira request depois disso leva ~30–50s. Aceitável para
> validação; para produção real, subir para um plano pago.

---

## 3. Frontend na Vercel

1. Vercel → **Add New** → **Project** → importe o repositório.
2. **Root Directory: `frontend`** (é um monorepo — passo obrigatório).
3. Framework: Next.js (detectado automaticamente).
4. Environment Variable:
   - `NEXT_PUBLIC_API_URL` = URL pública do Render
     (ex.: `https://ceap-connect-api.onrender.com`).
     > Variáveis `NEXT_PUBLIC_*` são inlinadas em **build time** — se mudar a
     > URL depois, é preciso um novo deploy (redeploy) na Vercel.
5. Deploy. A Vercel entrega o domínio, ex.: `https://ceap-connect.vercel.app`.

---

## 4. Fechar o ciclo (CORS)

1. No Render, edite `CORS_ORIGINS` para o domínio da Vercel:
   `https://ceap-connect.vercel.app`
   (múltiplas origens: separe por vírgula, sem espaços).
2. Salve — o Render redeploya automaticamente.
3. Acesse o domínio da Vercel, faça cadastro/login e confirme que o dashboard
   carrega os dados da API.

---

## Variáveis de ambiente (resumo)

### Backend (Render)
| Variável | Valor |
| --- | --- |
| `APP_ENV` | `production` |
| `DEBUG` | `false` |
| `DATABASE_URL` | `postgresql+asyncpg://...` (Neon) |
| `DATABASE_SSL` | `true` |
| `JWT_SECRET` | gerado pelo Render |
| `CORS_ORIGINS` | domínio da Vercel |
| `UVICORN_WORKERS` | `2` |

### Frontend (Vercel)
| Variável | Valor |
| --- | --- |
| `NEXT_PUBLIC_API_URL` | URL pública do Render |
