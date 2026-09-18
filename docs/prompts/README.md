# Registro de uso de IA no desenvolvimento

O edital do Projeto Integrador IV exige que **todo processo de engenharia de software feito com auxílio de IA seja registrado no repositório, com o prompt utilizado para a tarefa**. Esta pasta guarda esses registros.

Não confundir com `backend/app/llm/prompts/`, que guarda os prompts que o NutriSim usa em funcionamento (ver [`docs/arquitetura.md`](../arquitetura.md)).

## Regras

- **Um arquivo por tarefa**, com o nome `AAAA-MM-DD-descricao-curta.md`.
- **O prompt vai literal**, copiado e não resumido. Se a conversa teve várias mensagens relevantes, registre todas, na ordem.
- **Diga o que foi aproveitado e onde está:** arquivos, PR ou trecho do relatório.
- **Descreva a revisão humana:** o que a equipe conferiu, corrigiu ou descartou.
- **Nunca inclua** chaves de API, senhas ou dados pessoais.
- O registro entra **no mesmo PR** que traz o resultado da tarefa.

## Modelo

```markdown
# AAAA-MM-DD — Tarefa em poucas palavras

- **Autor(es):** 
- **Ferramenta e modelo:** (por exemplo, ChatGPT GPT-x, Claude Code com Claude Opus x, Gemini x)
- **Card:** NS-xxx
- **Tarefa:** o que se pediu à IA

## Prompt

> texto literal do prompt

## Resultado

O que a IA produziu e onde isso está no repositório.

## Revisão humana

O que foi conferido, alterado ou descartado pela equipe.
```
