# Hooks Globais

Hooks reutilizáveis por múltiplas features (ex.: `useMediaQuery`, `useDebounce`).

## Regras

- Um hook por arquivo, nome em `kebab-case` (ex.: `use-media-query.ts`).
- Hook específico de uma única feature vive em `features/<feature>/hooks`,
  nunca aqui.
- Sem regra de negócio de domínio — apenas lógica transversal de UI/estado.
