# 2026-10-28 — Validação do juiz do eval

- **Autor:** Arthur Pomarolli
- **Ferramenta e modelo:** Claude Code, com Claude Opus 5.5 (Anthropic)
- **Card:** NS-033
- **Tarefa:** sortear 30 respostas da primeira rodada do eval, montar uma planilha cega (sem o veredito do juiz) para rotular à mão, calcular a taxa de acerto do juiz contra os rótulos humanos e, como ficou abaixo de 85%, escrever o juiz-v3 e medir de novo.

## Prompt

Mensagem do autor, copiada sem alteração.

> vamos fazer o 33 então,
>
> Amostra de 30 vereditos para a C2 (50 até a rodada final, NS-064) rotulada pela equipe sem ver a classificação do juiz
>
> Taxa de acerto do juiz calculada (meta: pelo menos 85%)
>
> Se ficar abaixo da meta, prompt do juiz ajustado e acerto medido de novo
>
> Rótulos e resultado salvos em evals/juiz/

## Uso da IA na rotulagem

Os 30 rótulos de `evals/juiz/rotulos-c2.csv` foram feitos pelo autor, sem ver o veredito do juiz. Durante a rotulagem, a IA só explicou as regras das categorias, sem indicar a categoria de nenhuma linha.

## Testes

Os testes automáticos do backend passaram (198 de 199). A única falha é um teste de fora deste card, que no Windows lê a ficha de exemplo sem UTF-8.

O rejulgamento foi feito no computador do autor, com o juiz real (`gemini-3.5-flash-lite`, prompt `juiz-v3`), nas mesmas 30 respostas: 30 chamadas, cerca de 3 minutos, sem erro de cota. O acerto subiu de 50% (juiz-v2) para 86,7% (26 de 30), acima da meta de 85%.

## Resultado

- `backend/app/eval/validacao_juiz.py` e `evals/scripts/validar_juiz.py`: sorteio da amostra estratificada (semente 33), planilha cega, leitura dos rótulos, comparação com o juiz e rejulgamento com o prompt atual.
- `backend/tests/test_validacao_juiz.py`: testes do sorteio, da planilha e da comparação, sem chamar a API.
- `evals/juiz/amostra-c2.json`, `evals/juiz/rotulos-c2.csv`: a amostra e os rótulos do autor.
- `evals/juiz/resultado-c2_juiz-v2.json`: acerto do juiz-v2, 50% (15 de 30).
- `evals/juiz/juiz-v3.md` e `backend/app/eval/juiz.py`: prompt novo do juiz, que passa a ser o padrão.
- `evals/juiz/resultado-c2_juiz-v3.json`: acerto do juiz-v3, 86,7% (26 de 30), com as justificativas.
- `evals/juiz/relatorio-c2.md`: o relatório da validação.

## Revisão humana

Rotulei as 30 respostas na planilha, sem ver o veredito do juiz. Rodei o rejulgamento com o juiz-v3 no meu computador e conferi que o acerto subiu de 50% para 86,7%. Essa alteração foi feita com o intuito de melhorar a eficiência do modelo. Li o relatório e concordei com os erros e as limitações apontados.
