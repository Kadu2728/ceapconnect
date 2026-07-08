# Features

Cada funcionalidade de negócio (Autenticação, Dashboard, Missões, Conquistas,
Eventos, Notificações, Perfil...) vive em sua própria pasta dentro de
`features/`, seguindo a Feature-Based Architecture descrita em
`ARCHITECTURE.md` (raiz do projeto).

## Estrutura de uma feature

```
features/
  missoes/
    components/   # componentes de UI exclusivos da feature
    hooks/         # hooks específicos da feature (ex.: useMissoes)
    services/      # chamadas HTTP (axios) e integrações externas
    types/         # tipos e schemas (Zod) do domínio da feature
    utils/         # funções puras auxiliares da feature
```

## Regras

- Nunca misturar regra de negócio com componentes de UI — regra de negócio
  fica em `services` / `utils` / `hooks`; componentes apenas renderizam.
- Uma feature nunca importa arquivos internos de outra feature diretamente;
  o que precisa ser compartilhado sobe para `src/components`, `src/lib`,
  `src/hooks` ou `src/types`.
- A feature `landing/` (Fase 1 do ROADMAP.md) é a primeira implementada e
  segue esta estrutura: `components/` para as seções da página (Navbar,
  Hero, Pillars, Footer) e `types/` + `utils/` para tipos e constantes
  compartilhados entre elas. Não possui `hooks/` nem `services/` porque não
  há estado assíncrono nem regra de negócio — é conteúdo institucional
  estático.
