# CEAP Connect

Plataforma gamificada de Candidate Experience para o processo seletivo do CEAP — uma escola técnica gratuita para jovens em vulnerabilidade social.

**[Repositório](https://github.com/Kadu2728/ceapconnect)** · **[API em produção](https://ceap-connect-api.onrender.com/api/v1/health)** (Render) · Frontend em produção: Vercel

---

## O problema

O processo seletivo do CEAP perdia candidatos no meio do caminho, não na entrevista. O padrão observado: o jovem se inscreve, recebe pouco contato depois disso, esquece datas, perde prazos e simplesmente não aparece na prova. Cada evasão nessa fase é uma vaga gratuita que sobra sem ser preenchida, num programa desenhado justamente para quem mais precisa dela.

O problema não era falta de interesse — era falta de acompanhamento entre a inscrição e a prova.

## A história

**Julho de 2026 — setup e MVP.** Infraestrutura, landing page, autenticação e dashboard do candidato. A aposta inicial: transformar o processo seletivo em uma jornada digital — missões, progresso, conquistas — em vez de um formulário e um silêncio de semanas.

**Final de julho — gamificação com recompensas reais.** Recompensas de verdade (cursos, certificações) desbloqueadas por nível e conquista, assistente de IA para dúvidas do candidato, painel administrativo e onboarding guiado. A gamificação passou de "enfeite" para mecanismo de retenção.

**Agosto — o pitch para a direção e o sistema de predição de evasão (EPIC 14).** Depois de apresentar o produto para a direção do CEAP, o problema real ficou mais claro: não bastava engajar quem já estava engajado — era preciso identificar, *antes* da evasão acontecer, quem estava em risco de sumir. Nasceu o sistema de predição de evasão: um score de risco heurístico e explicável por candidato, alimentando um console de intervenção onde o coordenador vê a fila ordenada por risco, o motivo em português de cada score, e registra o contato feito. O candidato nunca vê o próprio score — a ferramenta é do coordenador, não um ranking exposto.

**Agosto (continuação) — experiência completa do candidato.** Upload de documentos, simulados com feedback imediato, aviso ao responsável sobre a entrevista, PWA instalável com push notifications, compartilhamento de conquistas, faixa de engajamento na coorte (deliberadamente sem ranking nominal), preferências de acessibilidade persistidas.

**Em andamento — de app de uma escola para plataforma.** Evolução do score heurístico para um modelo avaliado com harness de backtest (precision/recall/F1/AUC, versionamento, explicabilidade por atribuição de fatores), fila de risco em tempo real, e generalização multi-tenant: qualquer instituição parceira poderá rodar sua própria jornada, missões e recompensas na mesma plataforma, com isolamento total de dados por instituição.

## Como funciona

- **Jornada do candidato**: etapas, missões, progresso e conquistas gamificados — desenhado para ser elegante e profissional, nunca infantil.
- **Recompensas reais**: cursos e certificações de verdade, desbloqueados por nível/conquista, com fluxo de resgate e cumprimento pelo administrador.
- **Assistente de IA**: tira dúvidas do candidato sobre o processo seletivo (Google Gemini).
- **Sistema de predição de evasão**: score de risco explicável por candidato (fatores de inatividade, conclusão, ritmo, etapa travada, posição relativa à coorte) e console de intervenção para o coordenador agir antes da evasão acontecer.
- **PWA**: instalável, com push notifications reais.

## Stack

- **Frontend**: Next.js 16 (App Router) + React 19 + TypeScript + Tailwind + shadcn/ui + Framer Motion, arquitetura feature-based.
- **Backend**: FastAPI (async) + SQLAlchemy + PostgreSQL (Neon) + Alembic, arquitetura em camadas (API → Services → Repositories → Database).
- **Deploy**: Vercel (frontend) + Render (backend, Docker) + Neon (banco).

Detalhes técnicos completos em [ARCHITECTURE.md](./ARCHITECTURE.md).

## Rodando localmente

```bash
# Backend — porta 8000
cd backend && .venv/Scripts/uvicorn.exe app.main:app --host 127.0.0.1 --port 8000

# Frontend — porta 3000
cd frontend && npm run dev
```

Ou via `docker-compose.yml` na raiz, que sobe backend + frontend + Postgres local. Guia completo de variáveis de ambiente e deploy em [DEPLOY.md](./DEPLOY.md).

## Documentação

| Documento | Conteúdo |
| --- | --- |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Decisões técnicas, arquitetura do sistema de predição de evasão, plano de multi-tenancy |
| [PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md) | Visão de produto, público, princípios |
| [DATABASE.md](./DATABASE.md) | Modelagem do banco |
| [DEPLOY.md](./DEPLOY.md) | Guia de publicação em produção |
| [ROADMAP.md](./ROADMAP.md) | Fases do produto |
| [FRONTEND_GUIDELINES.md](./FRONTEND_GUIDELINES.md) / [BACKEND_GUIDELINES.md](./BACKEND_GUIDELINES.md) / [CODING_STANDARDS.md](./CODING_STANDARDS.md) | Padrões de código |

## Licença

Proprietário — todos os direitos reservados. Ver [LICENSE](./LICENSE).
