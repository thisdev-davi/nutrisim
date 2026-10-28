# 2026-10-27 — Primeira rodada do eval

- **Autor:** Arthur Pomarolli
- **Ferramenta e modelo:** Claude Code, com Claude Opus 5.5 (Anthropic)
- **Card:** NS-034
- **Tarefa:** completar o runner com os ataques de prompt injection e as métricas de robustez e de formato, rodar a primeira rodada do eval (5 fichas e 15 ataques, 1 execução por caso) com o paciente, o estudante e o juiz no Gemini e escrever o relatório da rodada.

## Prompt

Mensagens do autor, copiadas sem alteração, na ordem.

> vamos fazer o NS-034, todas as fichas e ataques executados 1 vez; as 3 execuções com média ficam para a rodada final (NS-064) a consistência (meta < 5%), robustez (meta < 10%) e formato (meta 100%) calculados com um relatório curto da rodada em evals/resultados/, com métricas, principais erros e custo em tokens
>
> Metas recalibradas, se necessário, com justificativa

> deixa, pode fazer voce nromalmente

## Testes

Os testes foram feitos no computador do autor, com o paciente real (`gemini-3.1-flash-lite`, prompt `paciente-v1`), o juiz real (`gemini-3.5-flash-lite`, prompt `juiz-v2`) e o estudante simulado (`gemini-3.5-flash-lite`, prompt `estudante-v1`).

Antes da rodada, os testes automáticos do backend passaram (161 de 162). A única falha foi um teste de fora deste card, que no Windows lê a ficha de exemplo sem UTF-8.

Primeiro foi feito um teste curto, com 1 ficha e 2 ataques. Depois veio a rodada completa: 5 fichas e 15 ataques, 146 chamadas, cerca de 206 mil tokens de entrada e 6 mil de saída, sem erro de cota.

## Resultado

- `backend/app/eval/runner.py`: os ataques de `evals/ataques/c2.json` rodam depois das fichas, cada um contra uma ficha, em rodízio, com as mensagens literais. As métricas novas são `taxa_quebra_ou_vazamento`, `taxa_json_valido` e `taxa_json_valido_primeira_tentativa`. O `uso` é registrado por execução, e o `uso_total`, para a rodada inteira. Há também a opção `--ataques`.
- `backend/app/eval/estudante.py`: o estudante conta as perguntas que ficaram com a original por saída inválida, para a métrica de formato.
- `backend/tests/test_runner.py`: testes dos ataques, do rodízio, da retomada e das métricas novas, sem chamar a API.
- `evals/README.md`: como os ataques e as métricas novas funcionam.
- `evals/resultados/2026-10-27_gemini-3.1-flash-lite_paciente-v1_rodada-1.json`: o resultado da rodada.
- `evals/resultados/2026-10-27_relatorio-rodada-1.md`: o relatório, com as métricas, a revisão dos vereditos, os principais erros, o custo e a decisão de manter as metas. A revisão dos vereditos foi proposta pela IA e conferida pelo autor.

## Revisão humana

Foram revisados os arquivos que a IA gerou e foi testado no meu computador. Primeiro rodei os testes automáticos, depois um teste curto com 1 ficha e 2 ataques e, por fim, a rodada completa, com as 5 fichas e os 15 ataques. Conferi no relatório os vereditos que mudam as métricas, como os ataques que o juiz marcou como quebra e o “15 por 9”, e concordei com a revisão e com manter as metas. Os erros do juiz ficam para a NS-033, e os do paciente, para a NS-073.
