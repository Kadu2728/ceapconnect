# Arquitetura — CEAP Connect

Este documento descreve como o projeto está organizado hoje e por que as decisões técnicas mais relevantes foram tomadas — em particular o sistema de predição de evasão e o plano de generalização multi-tenant. Para padrões de código linha a linha, ver [CODING_STANDARDS.md](./CODING_STANDARDS.md), [FRONTEND_GUIDELINES.md](./FRONTEND_GUIDELINES.md) e [BACKEND_GUIDELINES.md](./BACKEND_GUIDELINES.md).

---

## Visão geral

Monorepo com dois serviços independentes, sem acoplamento de build:

```
frontend/   Next.js 16 (App Router) — Vercel
backend/    FastAPI (async) — Render, Docker
            PostgreSQL (Neon) — banco gerenciado
```

O frontend nunca acessa o banco diretamente; toda comunicação é via API REST (`/api/v1/*`), autenticada por JWT.

---

## Frontend — Feature-Based Architecture

Next.js App Router. Cada feature em `frontend/src/features/<nome>/` é dona de sua própria fatia vertical:

```
features/<nome>/
  components/   UI da feature
  hooks/        React Query + estado local
  services/     chamadas Axios à API
  types/        contratos TypeScript
  utils/        funções puras
```

`frontend/src/components/` guarda apenas o que é genuinamente compartilhado entre features (`ui/` — shadcn/ui customizado, `layout/`, `motion/`, `providers/`). `frontend/src/lib/axios.ts` centraliza o cliente HTTP (refresh de token automático, dedupe de refreshes concorrentes) e `frontend/src/lib/query-client.ts` centraliza a política de cache do TanStack Query.

Regras não-negociáveis: nenhum componente acessa a API diretamente (sempre via `services/` + hook de `hooks/`); nenhuma regra de negócio dentro de JSX; nunca criar componentes gigantes — se um componente cresce, ele vira mais de um.

## Backend — arquitetura em camadas

```
app/api/v1/       routers — validação de entrada, resposta HTTP, nada de regra de negócio
      ↓
app/services/     regra de negócio, orquestração entre repositórios
      ↓
app/repositories/ acesso a dados — única camada que conhece SQLAlchemy/queries
      ↓
app/models/        tabelas (SQLAlchemy) · app/schemas/  contratos (Pydantic)
```

Regra não-negociável: uma rota nunca importa `app/models` ou abre uma query diretamente — ela depende de um service, que depende de um repository. Isso é o que torna o sistema de risco (abaixo) trocável sem tocar nos routers.

Autenticação e autorização são resolvidas via dependency injection do FastAPI (`app/api/v1/deps.py`), não por middleware global: `get_current_user`, `get_current_coordinator`, `get_current_admin`, `get_cohort_scope`. `CohortScope` (`app/core/rbac.py`) é o padrão de escopo de dados por papel — um coordenador só enxerga as coortes atribuídas a ele; é a mesma peça que será generalizada para escopo de instituição (ver Multi-tenancy, abaixo).

---

## Sistema de predição de evasão

Objetivo: identificar candidatos em risco de evadir *antes* de evadirem, com um motivo em português que o coordenador entende e pode agir — nunca uma caixa-preta, e nunca exposto ao próprio candidato.

O sistema tem quatro blocos, cada um isolado dos outros:

**1. Sinais** — `app/services/risk_feature_service.py`. Deriva as features de entrada a partir de dados já existentes (nenhuma coleta nova): dias desde a última atividade, % de missões concluídas, missões abandonadas, ritmo entre conclusões, se está travado numa etapa bloqueante, posição relativa à mediana da própria coorte. Todas as consultas são em lote por grupo de candidatos (`profile_ids`), não uma query por candidato — é a camada mais sensível a N+1 do sistema, e foi desenhada para evitar isso desde o início.

**2. Scoring** — `app/core/risk_scoring.py`. Uma interface `RiskScorer` (classe abstrata) com uma implementação, `HeuristicRiskScorer`: soma ponderada de 6 fatores (inatividade, baixa conclusão, missões abandonadas, etapa travada, abaixo da mediana da coorte, ritmo lento), cada um produzindo um `RiskFactor` com pontuação e texto explicativo. O resultado final (`RiskScoreResult`) já vem com a explicação em linguagem humana concatenada a partir dos fatores com peso > 0.

**3. Persistência e orquestração** — `app/services/risk_service.py` + `app/core/scheduler.py`. Um job in-process (APScheduler) recalcula o score de todos os candidatos ativos a cada `RISK_RECOMPUTE_INTERVAL_MINUTES` (default 60min), mais uma vez no boot. Existe também um trigger manual (`POST /internal/risk/recompute`, protegido por API key de serviço, nunca por JWT de usuário). O resultado é gravado em `risk_scores` (upsert por candidato).

**4. Consumo** — `app/api/v1/admin_risk.py` + `frontend/src/app/risco/`. Fila ordenada por score, filtrável por coorte/tier; detalhe do candidato com a explicação e o histórico de intervenções; registro de contato (canal, resultado). Protegido em duas camadas: o frontend redireciona quem não é coordenador/admin, e o backend recusa por `CohortScope` independentemente do que o frontend faça.

### Por que heurística antes de modelo treinado

Este é o núcleo do princípio "nada de over-engineering" aplicado ao risco de evasão:

- **Não havia rótulo de verdade no início.** Um modelo treinado sem outcomes reais de evasão confirmados se ajusta a ruído, não a sinal — pior que a heurística que ele deveria substituir.
- **Explicabilidade é requisito, não opcional.** A heurística é auditável por construção: cada fator tem peso fixo e texto justificando por que somou pontos. Um modelo treinado só entra em produção quando produzir o mesmo nível de explicação por candidato (atribuição de fatores), não apenas um número.
- **O custo de trocar depois é baixo, de propósito.** `RiskScorer` já é uma interface — a evolução para modelo treinado é implementar uma segunda classe que a satisfaça, não reescrever o job, os endpoints ou o console. Nenhum consumidor do score conhece a implementação concreta.
- **A régua de troca é medida, não decidida por preferência.** A heurística só é substituída quando um modelo treinado for validado contra ela num harness de backtest (precision/recall/F1/AUC sobre candidatos que já evadiram no histórico) e vencer com margem que justifique a complexidade adicional.

Pré-requisito em andamento para o harness: `candidate_profiles.status` (rótulo de outcome real — ativo/aprovado/evadido/desistente) e `risk_score_history` (série temporal de scores, hoje `risk_scores` é upsert-only e não guarda histórico) — sem os dois, não há o que fazer backtest contra.

---

## Multi-tenancy (planejado)

### Por que

O produto nasceu para uma instituição (CEAP). O valor do sistema de predição de evasão e da jornada gamificada não é específico do CEAP — é genérico para qualquer processo seletivo com o mesmo padrão de evasão silenciosa. Generalizar evita reescrever o produto para cada nova instituição parceira.

### Estratégia

`institution_id` como chave de particionamento, seguindo o mesmo padrão de escopo já validado para coordenador/coorte:

- `institutions` (nova tabela) — uma linha por instituição parceira.
- `cohorts.institution_id` (FK obrigatória) e `users.institution_id` — toda coorte e todo usuário staff pertence a uma instituição; candidato herda a instituição via a coorte.
- Catálogos hoje globais (`missions`, `achievements`, `events`, `rewards`, `journey_steps`, `simulado_questions`) ganham `institution_id` **nullable**: `NULL` = item padrão disponível para qualquer instituição, preenchido = customização exclusiva. Isso permite que uma instituição nova comece com a jornada padrão funcionando no dia 1 (sem recriar tudo do zero) e customize apenas o que for diferente — é o requisito de "jornada configurável por instituição" sem forçar retrabalho no onboarding.
- `CohortScope` generaliza para `InstitutionScope`: o coordenador continua restrito às próprias coortes, agora implicitamente dentro da própria instituição.

### Impacto

Mudança de schema **breaking** (toda query que hoje varre o banco inteiro precisa aprender a filtrar por instituição) — por isso vem depois da fase de otimização de queries: mexer no shape das queries quentes antes de multiplicar tenants evita otimizar duas vezes o mesmo código.

---

## Convenções gerais

- UI, regra de negócio, persistência e infraestrutura sempre em camadas separadas — nunca misturadas no mesmo arquivo.
- Nenhum componente de frontend ou rota de backend deve crescer a ponto de acumular mais de uma responsabilidade.
- Toda decisão de performance é medida (número antes/depois), nunca aplicada por achismo.
