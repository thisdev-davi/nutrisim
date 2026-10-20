# 2026-10-20 — Fichas de eval da C2

- **Autor:** Arthur Pomarolli
- **Ferramenta e modelo:** Claude (app), com Claude Opus 5.5 (Anthropic)
- **Card:** NS-027
- **Tarefa:** montar as 5 fichas de eval da C2, uma por perfil, no formato do `evals/README.md` (NS-017) e no schema da ficha (NS-014), com um teste que valida as fichas.

## Divisão do trabalho

- **Autor:** escolheu o paciente de cada perfil e os níveis de dificuldade, a partir de opções propostas pela IA, e revisou as fichas.
- **IA:** propôs as opções, montou as fichas em JSON com o roteiro de perguntas, escreveu o teste `backend/tests/test_fichas_eval.py` e validou as fichas contra o schema.

## Prompt

Foram sugeridas pela IA opções sobre as características de cada paciente, que foram analisadas e escolhidas conforme o autor julgou melhor para o trabalho, ocasionando assim a decisão das fichas de hipertensão, diabetes tipo 2, colesterol alto, idoso comendo pouco e jovem que quer emagrecer (encaminhamento).

Também foram definidos os níveis de dificuldade de cada um.

## Resultado

- `evals/fichas/`: 5 fichas (`adulto-hipertensao-facil-01`, `adulto-diabetes-tipo2-medio-01`, `adulto-dislipidemia-dificil-01`, `idoso-baixa-ingestao-medio-01` e `adulto-jovem-emagrecimento-medio-01`, este com conduta de encaminhamento).
- `backend/tests/test_fichas_eval.py`: valida cada ficha no schema `Ficha`, confere o número de omissões do nível (1, 3 ou 5, como em `content/perfis.md`) e verifica que toda omissão tem uma pergunta-gatilho no roteiro e que há uma pergunta de recusa.

## Revisão humana

Nesta etapa, juntamente com a IA, foram decididos os pacientes e a dificuldade de cada um, revisada a resposta da IA e alterado de acordo com o necessário.
