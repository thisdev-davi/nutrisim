# NutriSim

Simulador de pacientes com inteligência artificial para o ensino de Nutrição.

O estudante escolhe um perfil de paciente e um nível de dificuldade. Em seguida, conduz a anamnese em uma conversa em tempo real com um paciente simulado por LLM e monta um plano alimentar. Por fim, vê como esse plano se comportaria com adesão ideal e com adesão realista.

> **Fase atual:** planejamento (Checkpoint 1). O repositório ainda não tem código de aplicação. A organização do trabalho está em [`docs/`](docs/).

## Como funciona

A regra central da arquitetura é a divisão de responsabilidades: **a IA representa o comportamento do paciente, e um motor determinístico calcula a fisiologia**. O LLM nunca inventa números de composição, gasto energético ou peso. Esses valores vêm da TACO e de equações publicadas.

| Etapa | O que acontece | Quem atua |
|---|---|---|
| 1. Caso | O estudante escolhe o perfil e a dificuldade, e o sistema gera uma ficha oculta | Estudante → IA |
| 2. Anamnese | Entrevista em tempo real com o paciente simulado | Estudante ↔ IA |
| 3. Plano alimentar | O estudante monta o plano com busca na TACO, e o motor calcula nutrientes e GET e confere as restrições | Estudante → motor |
| 4. Cenários | A IA define a adesão realista, e o motor projeta o peso e a adequação: ideal × real | IA → motor |
| 5. Retorno e feedback | O paciente relata as dificuldades, e a rubrica gera o feedback | IA → estudante |

O fluxo completo, em raias, está na [Figura 1 do relatório](docs/relatorios/fluxo.png). Os detalhes técnicos estão em [`docs/arquitetura.md`](docs/arquitetura.md).

## Estrutura do repositório

```text
nutrisim/
├── backend/      API FastAPI, motor de cálculo e integração com LLM
├── frontend/     aplicação Next.js responsiva
├── content/      rubricas e roteiros de anamnese em Markdown
├── evals/        fichas, ataques, prompt do juiz, scripts e resultados
├── docs/         relatórios, arquitetura, decisões, sprints e quadro de tarefas
│   └── prompts/  registro dos prompts de IA usados no desenvolvimento
└── .github/      templates de issue e PR (e, a partir da Sprint 1, a CI)
```

Cada pasta tem um README que descreve a estrutura interna prevista.

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Frontend | Next.js (React) e Tailwind CSS |
| Backend | FastAPI (Python) |
| Banco de dados | PostgreSQL (Neon) |
| IA | Gemini Flash via Google AI Studio (paciente) e Groq (juiz do eval) |
| Testes | pytest e Playwright |
| Integração contínua | GitHub Actions |
| Deploy | Render |

As justificativas estão em [`docs/decisoes.md`](docs/decisoes.md).

## Documentação

| Documento | Conteúdo |
|---|---|
| [Relatório C1](docs/relatorios/NutriSim_Relatorio_C1.md) | escopo, justificativa, metodologia e plano de trabalho |
| [Arquitetura](docs/arquitetura.md) | componentes, fronteiras entre IA e motor, árvore de pastas |
| [Decisões](docs/decisoes.md) | registro das decisões de arquitetura (ADRs) |
| [Sprints](docs/sprints.md) | calendário, metas e critérios de saída de cada sprint |
| [Quadro de tarefas](docs/kanban.md) | todos os cards, prontos para o GitHub Projects |
| [Entregas do edital](docs/entregas-projeto-integrador-iv.md) | prazos, rubricas de avaliação e requisitos obrigatórios |
| [Registro de uso de IA](docs/prompts/README.md) | prompts usados no desenvolvimento (integridade acadêmica) |
| [Como contribuir](CONTRIBUTING.md) | branches, commits, pull requests e definição de pronto |

## Equipe

| Integrante | Responsabilidade principal |
|---|---|
| Arthur Pomarolli | Frontend responsivo e experiência de uso |
| Davi de Souza | Backend e integração com LLMs |
| Mauro Barros | Motor de cálculo determinístico e testes automatizados |
| Pedro Augusto | Harness de avaliação, métricas e governança de IA responsável |

## Entregas

| Checkpoint | Entrega | Prazo |
|---|---|---|
| C1 | Relatório e repositório inicial | 18/09/2026 |
| C2 | Vídeo do protótipo com a IA funcionando e os primeiros testes e eval | 30/10/2026 |
| C3 | MVP publicado, vídeo, documentação, testes, eval e análise de impacto | 04/12/2026 |

## Uso de IA no desenvolvimento

O edital exige registrar todo uso de IA na engenharia de software. Cada tarefa feita com ajuda de IA ganha um arquivo em [`docs/prompts/`](docs/prompts/) com o prompt utilizado.

## Contexto acadêmico

Projeto Integrador IV (Aplicações de Inteligência Artificial), curso de Ciência da Computação do Centro Universitário FAESA, 2026/2. Professor: Prof. M.Sc. Howard Cruz Roatti.

O NutriSim é uma ferramenta educacional. Ele não se destina a atender pacientes reais nem a apoiar decisões clínicas, e todos os casos são sintéticos.
