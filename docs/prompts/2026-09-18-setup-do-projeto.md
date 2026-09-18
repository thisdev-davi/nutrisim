# 2026-09-18 — Setup do repositório: pastas, arquitetura, sprints e cards

- **Autor:** Davi de Souza
- **Ferramenta e modelo:** Claude Code, com Claude Opus 5 (Anthropic)
- **Card:** NS-001 e NS-002 (Sprint 0 — C1)
- **Tarefa:** montar o setup do projeto, sem código de aplicação: estrutura de pastas, documentação de arquitetura, divisão em sprints até a C3 e cards do quadro kanban.

## Contexto fornecido à IA

- `NutriSim_Relatorio_C1.md` (relatório da C1)
- `fluxo.png` (Figura 1 do relatório)
- `entregas-projeto-integrador-iv.md` (resumo do edital)

## Prompt

> Claude, eu estou fazendo um trabalho academico que está descrito nesse documento @NutriSim_Relatorio_C1.md @fluxo.png , e preciso que você me ajude a montar todo um setup do projeto ( sem mexer nada de código agora ). Focando em fazer as arquiteturas de pastas, cards kanban ( vamos fazer um .md para isso e depois vou jogar no projects do gitlab ) e separar o projeto em sprints até a data do projeto.

A primeira resposta foi interrompida pelo limite de saída. A conversa seguiu com a mensagem:

> Continue

## Perguntas da IA e respostas do autor

| Pergunta                                                                                                                                                                      | Resposta                                                                           |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| O edital exige o repositório no GitHub, e o relatório cita GitHub Projects e GitHub Actions, mas você falou em "projects do gitlab". Onde vão ficar o repositório e o quadro? | GitHub                                                                             |
| Até que profundidade eu crio as pastas agora, sem código nenhum?                                                                                                              | Nível do relatório + READMEs (subpastas criadas junto com o primeiro arquivo real) |

Depois disso, o autor aprovou o plano de execução proposto pela IA.

## Resultado

Criados:

- `README.md`, `CONTRIBUTING.md`, `.gitignore`
- `.github/pull_request_template.md`, `.github/ISSUE_TEMPLATE/tarefa.md`, `.github/ISSUE_TEMPLATE/bug.md`
- `backend/README.md`, `frontend/README.md`, `content/README.md`, `evals/README.md`
- `docs/arquitetura.md`, `docs/decisoes.md`, `docs/sprints.md`, `docs/kanban.md` (69 cards)
- `docs/prompts/README.md` e este registro

Movidos, sem alteração de conteúdo:

- `NutriSim_Relatorio_C1.md` e `fluxo.png` → `docs/relatorios/`
- `entregas-projeto-integrador-iv.md` → `docs/`

## Revisão humana

- [ ] Datas das sprints e responsáveis dos cards conferidos pelo grupo
- [ ] Critérios de aceite revisados por cada integrante na própria área
- [ ] Ajustes feitos antes do primeiro commit registrados aqui
