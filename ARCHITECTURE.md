# Arquitetura

O projeto deve seguir Feature Based Architecture.

## Frontend

Next.js App Router

Features independentes.

Cada feature possui:

- components
- hooks
- services
- types
- utils

Nunca criar componentes gigantes.

Toda regra de negócio deve permanecer fora da interface.

---

## Backend

FastAPI

Arquitetura em camadas.

API

↓

Services

↓

Repositories

↓

Database

Nunca acessar o banco diretamente pela rota.

---

## Organização

Separar claramente:

UI

Business

Persistence

Infrastructure

---

Sempre priorizar escalabilidade.
