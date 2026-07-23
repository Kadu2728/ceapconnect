# CEAP Connect — Retomada (handoff)

> Guia rápido para continuar amanhã. Todo o código está salvo em disco.

## Como rodar (2 processos)

Abra dois terminais na pasta do projeto:

**Backend (API + IA + admin) — porta 8000**
```bash
cd backend && .venv/Scripts/uvicorn.exe app.main:app --host 127.0.0.1 --port 8000
```

**Frontend (Next.js) — porta 3000**
```bash
cd frontend && npm run dev
```

Depois abra: **http://localhost:3000**

> Os dois estão configurados em `.claude/launch.json` (nomes `frontend` e `backend`).

## Como entrar

- **Sua conta** `kacadu007@gmail.com` (é **admin** → vê o menu "Admin" e o painel).
- Conta de teste admin: `maria_1783467492@example.com` / `Senha1234`.
- Conta de teste aluno: `teste_1783465836@example.com` / `Senha1234`.

## O que ver funcionando

- **Landing** nova (marca real do CEAP-SP, azul/verde/roxo/laranja) em `/`.
- **App do candidato**: Dashboard, Missões (concluir → XP + conquista), Conquistas, Eventos (inscrever → notificação).
- **Bot de IA**: bolha flutuante no canto (área logada). Responde uma mensagem de "não configurado" até a chave ser adicionada (abaixo).
- **Painel admin** em `/admin` (só admin): acesso/engajamento dos alunos + gráfico de cadastros.
- **Boas-vindas** no primeiro login + transições suaves entre páginas.

## Pendência única para o bot responder de verdade

O bot usa o **Groq (nível gratuito)**. Cole a chave em `backend/.env`
(o slot já existe):
```
GROQ_API_KEY=gsk_...
```
Reinicie o backend. Pegue a chave GRÁTIS (sem cartão) em https://console.groq.com/keys
(O Gemini foi descartado: a conta do usuário tem free tier = 0.)

## Próximos passos sugeridos

- Central de **Notificações** e tela de **Perfil** (modelos já existem no backend).
- Deploy (Vercel para o front, Render/Railway para o back, Neon já é o banco).

## Estado de qualidade

`ruff` · `typecheck` · `lint` · `next build` — todos limpos. Migrations aplicadas no Neon.
Nada foi commitado ainda (preferência de seguir iterando) — quando quiser, é só pedir o commit.
