# 2026-10-20 — Fichas de eval da C2

- **Autor:** Arthur Pomarolli
- **Ferramenta e modelo:** Claude (app), com Claude Opus 5.5 (Anthropic)
- **Card:** NS-027
- **Tarefa:** montar as 5 fichas de eval da C2, uma por perfil, no formato do `evals/README.md` (NS-017) e no schema da ficha (NS-014), com um teste que valida as fichas.

## Divisão do trabalho

- **Autor:** escolheu o paciente de cada perfil e os níveis de dificuldade e revisou as fichas.
- **Ajustes decididos pelo autor na revisão:** tirar a contradição do lanche da Patrícia (o erro previsto passou a ser o óleo), trocar a pergunta "O que vai na sua marmita?" do Jorge por "Que horas você acorda?", reescrever a pergunta de recusa da Camila para "Quantas calorias você acha que precisa comer por dia para emagrecer?" e, para equilibrar gênero e renda, trocar a paciente idosa por um homem (Antônio) e subir o orçamento da Patrícia para R$ 3.000. A conferência do `perfil_id` com a lista de perfis do backend chegou a ser feita, mas o autor decidiu tirá-la, porque essa lista ainda é provisória (mock até a NS-019) e o teste quebraria quando ela mudasse de lugar.
- **Revisão do PR #100 (Davi):** as correções pedidas foram feitas pela IA, com aprovação do autor: imprecisões que contradiziam omissões (Patrícia e Jorge), campos que vazavam omissões (Patrícia e Antônio), informações que o roteiro pedia e a ficha não tinha (tempero e álcool na Rosângela, mastigação no Antônio), perguntas `omitir` próximas demais do recordatório, a pergunta de recusa da Camila e novas conferências no teste. Na mesma revisão, a IA aplicou as mesmas regras às outras fichas: recusas do Jorge e da Patrícia pedindo o número do exame em vez da opinião, a imprecisão do Antônio (que tocava a omissão do almoço), perguntas `omitir` do Antônio e da Patrícia, a frase da Camila que antecipava a omissão de evitar comer com outras pessoas e o consumo de álcool nas fichas que não o informavam.
- **IA:** propôs as opções, montou as fichas em JSON com o roteiro de perguntas, escreveu o teste `backend/tests/test_fichas_eval.py` e validou as fichas contra o schema.

## Prompt

Mensagens do autor, na ordem, copiadas sem alteração. Onde a IA fez uma pergunta com opções, aparece a opção escolhida.

> confira o repositorio novamente e ve se o NS-027 ainda falta, se faltar, ve se ainda e possivel fazer ele

A IA propôs duas opções de paciente por perfil. Escolhas do autor:

> Hipertensão A
>
> Diabetes tipo 2 A
>
> Idoso comendo pouco B
>
> Jovem que quer emagrecer (encaminhamento) A

| Pergunta da IA | Opção escolhida |
|---|---|
| Faltou o perfil de colesterol alto. Qual paciente você quer? | B: mulher, 44, churrasco |
| Quais níveis de dificuldade você quer para os 5 pacientes? | Usar a sugestão (hipertensão fácil, diabetes médio, colesterol difícil, idoso médio, jovem médio) |

Resposta à pergunta da IA sobre manter o teste em `backend/tests/` (opção 1, manter e avisar no PR):

> 1

Revisão das fichas pela IA, pedida pelo autor:

> /grill-me Claude, com o meu novo workflow, revise as tarefas que acabou de criar. Usando os plugins e procurando skills

> certo, o que devemos alterar ?

> Vamos fazer as seguintes alterações então:
>
> Patrícia: tirar a contradição do lanche
> Trocar o erro previsto que confunde o juiz:
>
> substituir:
> “esquece de citar o lanche da praça de alimentação e só lembra quando o estudante pergunta do horário de trabalho”
>
> Por:
> “diz que usa ‘um fiozinho’ de óleo, mas frita tudo”
>
> Jorge: trocar a pergunta que pode revelar o segredo
>
> Substituir:
> “O que vai na sua marmita?” (não pode revelar o refrigerante)
>
> Por:
> “Que horas você acorda?” (não pode revelar o refrigerante)
>
> Teste: conferir o nome do perfil
> Acrescentar uma linha que compara o `perfil_id` de cada ficha com a lista dos 5 perfis do backend. Um nome digitado errado passa a fazer o teste falhar.
>
> e na 4, fazer as duas

> pode adicionar o item 7 também

> ok, pode ser a B, fora isso, alguma coisa nos outros documentos que vão para o git hub foram alterados ?

Correção da revisão do Davi no PR #100:

> revise o que foi pedido pelo davi, o que tiver de erros, corrija

## Resultado

- `evals/fichas/`: 5 fichas (`adulto-hipertensao-facil-01`, `adulto-diabetes-tipo2-medio-01`, `adulto-dislipidemia-dificil-01`, `idoso-baixa-ingestao-medio-01` e `adulto-jovem-emagrecimento-medio-01`, este com conduta de encaminhamento).
- `backend/tests/test_fichas_eval.py`: valida cada ficha no schema `Ficha`, confere o número de omissões do nível (1, 3 ou 5, como em `content/perfis.md`) e verifica que toda omissão tem uma pergunta-gatilho no roteiro, que nenhum `omitir` vem depois do `revelar` do mesmo item, que há uma pergunta de recusa, que o id termina em `-NN`, que a postura bate com o nível e que existe pelo menos um caso de encaminhamento.

## Revisão humana

Nesta etapa, juntamente com a IA, foram decididos os pacientes e a dificuldade de cada um, revisada a resposta da IA e alterado de acordo com o necessário.
