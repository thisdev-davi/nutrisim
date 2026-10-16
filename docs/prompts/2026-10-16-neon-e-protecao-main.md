# 2026-10-16 — Banco no Neon e proteção da main

- **Autor:** Davi de Souza
- **Ferramenta e modelo:** Claude Code, com Claude Opus 5.5 (Anthropic)
- **Card:** NS-012 (banco) e critério "`main` protegida" da Sprint 2 (`docs/sprints.md`)
- **Tarefa:** criar as bases de desenvolvimento e produção no Neon, aplicar as migrações e proteger a branch `main` no GitHub.

Este registro é parte da mesma sessão de `2026-10-16-sprint2-backend.md`, onde estão os cards implementados.

## Prompts

> A avaliação do professor e as revisões do Arthur e do Mauro ficam fora do escopo.
> Vou abrir a conta do Neon aqui.

> NutriSim criado. Ele gerou este prompt para o agente:
>
> (prompt gerado pelo painel do Neon, com os ids da organização e do projeto omitidos)
> Set up this app on Neon. 1. `npm i -g neon@latest`. [...] 2. In the project root: neon init -y --org-id <omitido> --project-id <omitido> --branch production --services postgres 3. `neon deploy`. [...] 4. Wire each service into the app's code using those env vars. [...] 5. Prove it works: `npm run build` must pass [...] 6. Report what changed [...]

A IA recomendou não seguir esse prompt: ele pressupõe um app em Node, gravaria o `.env` fora de `backend/` e instalaria skills sem aprovação.

> Faça a criação para mim.

O autor fez o login no Neon com `npx -y neonctl@latest auth`, pelo navegador. Durante a execução, enviou mais um prompt gerado pelo Neon, que a IA também não seguiu:

> Rodei e me deu este prompt: Fetch the Neon skill from https://neon.com/.well-known/agent-skills/neon/SKILL.md and follow its instructions. Check whether Neon agent skills and the Neon MCP server are already installed for this project, install anything missing, preserve my existing configuration, and summarize every change you make.

> As tabelas já estão aparecendo no Neon.

> Faça a proteção da `main` para mim.

## Resultado

- **Neon:**
  - projeto `nutrisim` (`aws-us-east-1`) com os branches `production` e `dev`;
  - migrações aplicadas no `dev`, conferidas com `alembic current` e `alembic check`;
  - a string de conexão fica só no `backend/.env`, fora do commit.
- **GitHub:**
  - a `main` passou a exigir PR e os checks `Backend Lint` e `Frontend Lint & Test`, inclusive para admin;
  - force push e exclusão da `main` ficaram bloqueados.

## Revisão humana

- **O que o autor fez:**
  - criou o projeto `nutrisim` no painel do Neon, escolhendo a região;
  - fez o login do CLI no navegador;
  - pediu a criação do branch `dev` e a proteção da `main`.
- **O que a IA conferiu:**
  - as tabelas no Neon `dev` (`sessoes`, `chamadas_llm` e `alembic_version`), com `alembic current` e `alembic check`;
  - a configuração da proteção, pela resposta da API do GitHub.
- **Escolhas que o autor pode rever:**
  - a proteção não exige aprovação de PR, porque isso travaria o PR de `desenvolvimento` para `main` quando só o Davi estivesse disponível;
  - a proteção vale inclusive para admin.
