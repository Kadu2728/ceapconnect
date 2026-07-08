# CEAP Connect — Frontend

Aplicação web (Next.js 16 + React 19 + TypeScript) do CEAP Connect.

## Stack

- Next.js 16 (App Router, Server Components por padrão)
- React 19
- TypeScript (`strict`)
- Tailwind CSS v4
- shadcn/ui (estilo `new-york`, base do Design System)
- Framer Motion
- TanStack Query, Zustand, Axios
- React Hook Form + Zod
- next-themes (tema light / dark / automático)

## Scripts

| Comando                | Descrição                                |
| ---------------------- | ---------------------------------------- |
| `npm run dev`          | Servidor de desenvolvimento (Turbopack)  |
| `npm run build`        | Build de produção                        |
| `npm run start`        | Sobe o build de produção                 |
| `npm run lint`         | ESLint                                   |
| `npm run typecheck`    | Checagem de tipos sem emitir arquivos    |
| `npm run format`       | Formata o código com Prettier            |
| `npm run format:check` | Verifica formatação sem alterar arquivos |

## Estrutura

```
src/
  app/          # Rotas (App Router)
  components/
    ui/         # Primitivas shadcn/ui (Button, Card, Input...)
    theme/      # Componentes de tema (ThemeToggle)
    providers/  # Providers globais (Query, Theme)
  features/     # Features de negócio (Feature-Based Architecture)
  hooks/        # Hooks globais reutilizáveis
  lib/          # Axios, Query Client, utils transversais
  styles/       # Design tokens (CSS variables)
  types/        # Tipos globais compartilhados
```

Consulte `ARCHITECTURE.md`, `FRONTEND_GUIDELINES.md` e `DESIGN_SYSTEM.md` na
raiz do repositório para as convenções obrigatórias do projeto.

## Variáveis de ambiente

Copie `.env.example` para `.env.local` e ajuste conforme necessário.

## Setup

```bash
npm install
npm run dev
```
