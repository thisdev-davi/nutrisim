# 2026-10-27 — Estudante simulado do eval

- **Autor:** Arthur Pomarolli
- **Ferramenta e modelo:** Claude Code, com Claude Opus 5.5 (Anthropic)
- **Card:** NS-031
- **Tarefa:** criar o estudante simulado do eval, um LLM no papel de estudante de Nutrição que conduz a entrevista com o paciente simulado a partir do roteiro da ficha, com a conversa salva junto ao resultado e um limite de turnos para controlar o custo.

## Prompt

Mensagem do autor, copiada sem alteração.

> Vamos fazer o NS-31, começando com LLM no papel de estudante, conduzindo a entrevista a partir do roteiro da ficha, conversa completa salva junto ao resultado, número de turnos limitado, para controlar o custo

## Testes

Os testes foram feitos no computador do autor (Windows), com a ficha `adulto-hipertensao-facil-01` (7 perguntas), o paciente real (`gemini-3.1-flash-lite`, prompt `paciente-v1`), o juiz real (`gemini-3.5-flash-lite`, prompt `juiz-v2`) e o estudante simulado no mesmo modelo do juiz (prompt `estudante-v1`).

Antes da rodada, os testes automáticos do backend passaram (156 de 157). A única falha foi um teste antigo, de fora deste card, que no Windows lê a ficha de exemplo sem UTF-8.

A rodada levou 1min34s, sem nenhum veredito com falha e com taxa de inconsistência 0. O estudante reformulou as 7 perguntas sem mudar o tema e retomou o que a paciente tinha dito ("Com base na sua rotina corrida de trabalho…"). Na pergunta sobre o café da manhã, ele não puxou o assunto dos beliscos, e a paciente não revelou a omissão. Na pergunta-gatilho, a paciente revelou que prova as panelas e belisca torresmo e farofa. Na pergunta do limite de sal, ele continuou pedindo o número, e a paciente recusou sem sair do personagem. O estudante gastou 7 chamadas, com cerca de 4,6 mil tokens de entrada e 200 de saída.

## Resultado

- `backend/app/eval/estudante.py`: a interface `Estudante` (a conversa e o passo do roteiro entram, a pergunta sai), o `EstudanteRoteiro`, que faz a pergunta do roteiro como está, sem LLM, e o `EstudanteLLM`, que reformula a pergunta no Gemini sem mudar o tema. O estudante não recebe a ficha nem o `esperado` e o `item` do passo.
- `evals/estudante/estudante-v1.md`: o prompt do estudante.
- `backend/app/eval/runner.py`: as opções `--estudante` (`roteiro` ou `llm`) e `--max-turnos` (padrão 10). A conversa guarda a pergunta feita e a do roteiro, e o resultado registra o modelo e o prompt do estudante.
- `backend/tests/test_estudante.py`: testes com o Gemini falso, sem chamar a API.
- `evals/README.md`, `backend/README.md` e `backend/.env.example`: como usar e a variável `LLM_MODELO_ESTUDANTE` (vazia, usa o modelo do juiz).

## Revisão humana

Foram revisados os arquivos que a IA gerou e foi testado no meu computador. Primeiro rodei os testes automáticos e depois fiz uma rodada de verdade, com o paciente, o juiz e o estudante no Gemini. As perguntas mudaram de jeito, mas continuaram no mesmo assunto. Também conferi se este card ia dar conflito com o runner da NS-026.
