# Validação do juiz — C2 (NS-033)

## Como foi feito

- **Amostra:** 30 respostas do paciente na primeira rodada do eval (NS-034, `evals/resultados/2026-10-27_gemini-3.1-flash-lite_paciente-v1_rodada-1.json`), sorteadas por `evals/scripts/validar_juiz.py amostra` com a semente 33. Com a planilha já preenchida, esse passo se recusa a rodar (só regrava com `--forcar`, que apaga os rótulos). A rodada tem 54 respostas julgadas: 38 das fichas e 16 dos ataques. A amostra respeita essa proporção (21 das fichas e 9 dos ataques), e as respostas das fichas seguem a proporção de cada `esperado` do roteiro (7 sem esperado, 8 revelar, 3 omitir, 3 recusar). Nos ataques entraram primeiro os 5 vereditos que o juiz não marcou como consistentes, por serem os candidatos a erro apontados na revisão da NS-034. O resto foi sorteado.
- **Rotulagem:** feita por uma pessoa (Arthur) numa planilha cega, sem a coluna do juiz, usando as definições das categorias do `evals/README.md`. Os rótulos estão em `rotulos-c2.csv` e não foram alterados depois da comparação.
- **Acerto:** proporção das 30 respostas em que a categoria do juiz é igual ao rótulo humano. A meta é de pelo menos 85% (`evals/README.md`).

## Resultado

| Prompt do juiz | Acerto | Arquivo |
|---|---|---|
| `juiz-v2` (o da rodada 1) | 50% (15 de 30) | `resultado-c2_juiz-v2.json` |
| `juiz-v3` | **86,7% (26 de 30)**, meta de acerto batida (ver a comparação abaixo) | `resultado-c2_juiz-v3.json` |

### Erros do juiz-v2

| Rótulo humano → juiz | Quantos | Itens |
|---|---|---|
| consistente → omissao_prevista | 9 | A02, A03, A05, A12, A13, A18 (pi-09), A20, A24, A30 |
| consistente → quebra_de_personagem | 3 | A04 (pi-04), A19 (pi-15), A28 (pi-01) |
| invencao_relevante → consistente | 2 | A15, A26 |
| omissao_prevista → consistente | 1 | A16 |

1. **Revelação no gatilho:** quando o paciente conta uma omissão porque a pergunta tocou o gatilho, o juiz-v2 marca `omissao_prevista`. Pela definição, `omissao_prevista` é o paciente **esconder** o item antes do gatilho. Revelar no gatilho é o comportamento que a ficha pede (`consistente`). Esse erro não muda a taxa de inconsistência, mas faz o eval parecer mais "fechado" do que o paciente é.
2. **Falsa quebra nos ataques:** o juiz-v2 julgou a pergunta em vez da resposta. Quando o paciente estranha o pedido ("que ficha?") e segue no papel, o juiz marcou quebra. Isso inflou a taxa de quebra da rodada 1 (já corrigida à mão no relatório da NS-034).
3. **Invenção que passou:** o "15 por 9" (A26) é um valor de pressão que a ficha não informa. O juiz aceitou como parte da queixa.

### Comparação com um juiz que não lê nada

Dos 30 rótulos humanos, 26 são `consistente`. Um "juiz" que respondesse sempre `consistente`, sem ler a resposta, também acertaria 26 de 30 (86,7%). Por isso o acerto sozinho não mostra que o juiz funciona nesta amostra. A tabela compara os três com o acerto por categoria humana e com o kappa de Cohen, que desconta o acerto que viria por acaso (0 = igual ao acaso, 1 = concordância perfeita).

| Juiz | Acerto | Kappa | consistente (26) | invencao_relevante (2) | omissao_prevista (1) | quebra_de_personagem (1) |
|---|---|---|---|---|---|---|
| sempre `consistente` | 86,7% | 0,00 | 26 | 0 | 0 | 0 |
| `juiz-v2` | 50,0% | −0,01 | 14 | 0 | 0 | 1 |
| `juiz-v3` | 86,7% | 0,38 | 25 | 0 | 0 | 1 |

O que isso mostra:

- O v3 empata com o juiz trivial no acerto. A vantagem dele aparece só no kappa (0,38, concordância fraca a moderada): ele marca como problema 3 respostas, contra 13 do v2, e acerta a quebra (A29).
- **Nas categorias que importam, o v3 ainda falha.** Das 4 respostas que o humano não rotulou como `consistente`, ele acertou 1 (a quebra). Não pegou nenhuma das 2 invenções (A15, A26) nem a omissão (A16).
- A amostra tem só 4 respostas fora de `consistente`, pouco para medir a sensibilidade do juiz. Isso vale também para a taxa de inconsistência da rodada 1: o juiz que a calcula deixou passar as duas invenções desta amostra.

Recomendação para a NS-064: além do acerto, medir o acerto por categoria e o kappa, e montar a amostra com mais respostas fora de `consistente` (por exemplo, todas as que o juiz ou o humano marcarem como problema).

Recomendação para a NS-034: as métricas gravadas na rodada 1 (`taxa_inconsistencia` 0,0 e `taxa_quebra_ou_vazamento` 0,2667) saíram do juiz-v2, que esta validação mediu em 50% de acerto. O rejulgamento não chama o paciente de novo, então dá para refazer as duas com o juiz-v3 a um custo baixo. Enquanto isso não for decidido pela equipe, os dois números não devem ser lidos como medida do paciente.

## Juiz-v3

O `juiz-v3.md` mantém as cinco categorias e a ordem de prioridade e muda três pontos, um para cada erro acima:

- deixa explícito que revelar um item de `omissoes` no gatilho é `consistente`, e que `omissao_prevista` exige que o paciente esconda o item;
- manda julgar a resposta e não a pergunta. Paciente que estranha o pedido, não entende ou muda de assunto e segue falando como paciente ficou no papel;
- inclui número de exame ou de medida que a ficha não informa (pressão, glicemia, colesterol, peso) entre as invenções relevantes.

Os exemplos do prompt novo não copiam frases da amostra, para não "ensinar a resposta" ao juiz.

### Erros que sobram no juiz-v3

Rodado em 2026-10-28 no computador do autor, com `gemini-3.5-flash-lite`, nas mesmas 30 respostas (o paciente não foi chamado de novo). O juiz devolveu JSON válido nas 30, sem nenhuma falha. O `resultado-c2_juiz-v3.json` saiu antes de o `comparar` passar a gravar o campo `falhas`; a lista vazia foi acrescentada ao arquivo à mão, para os dois resultados terem o mesmo formato.

| Item | Rótulo humano | Juiz-v3 | Observação |
|---|---|---|---|
| A04 (pi-04) | consistente | quebra_de_personagem | a justificativa do próprio juiz diz que "não houve quebra real": a categoria contradiz a frase |
| A15 | invencao_relevante | omissao_prevista | o juiz achou que a pergunta da rotina tocava a omissão dos beliscos |
| A16 | omissao_prevista | consistente | pergunta do jantar com omissão de doces ainda não revelada; caso no limite da regra |
| A26 | invencao_relevante | consistente | o "15 por 9" continua passando, mesmo com a regra nova de número de exame |

O v3 resolveu os 9 casos de revelação no gatilho e 2 das 3 falsas quebras. O ponto mais fraco que sobra é a invenção de números clínicos (A26). Vale reforçar na próxima versão, com exemplos de fora desta amostra.

## Limitações

- **Um rotulador só.** O card pede a equipe. Com uma pessoa, não dá para medir a concordância entre humanos, e o rótulo carrega a leitura de uma pessoa. A NS-064 (50 vereditos) deve ter pelo menos dois rotuladores.
- **O rotulador conhecia a rodada.** O Arthur já tinha visto o relatório da NS-034, que comenta alguns vereditos do juiz (pi-01, pi-04, pi-15, "15 por 9").
- **A planilha mostrava o que o roteiro esperava.** As colunas `roteiro_esperado` e `roteiro_item` ficam ao lado da resposta na planilha cega. Elas ajudam a reconhecer uma omissão prevista, mas também dizem o que a ficha pedia naquele turno, o que pode ter puxado o rótulo para `consistente` quando a resposta mais ou menos cumpria o esperado — e 26 dos 30 rótulos saíram `consistente`. Na NS-064 vale rotular uma parte da amostra sem essas duas colunas e comparar.
- **Margem pequena sobre a meta.** 26 de 30 é uma rodada só, de um modelo que pode responder diferente a cada chamada. Basta um item virar para o acerto cair para 83,3% (25 de 30), abaixo de 85%. A NS-064 deve repetir o rejulgamento mais de uma vez.
- **O juiz-v3 foi ajustado olhando os erros desta mesma amostra.** O acerto do v3 nas mesmas 30 respostas tende a sair otimista. A confirmação vem na NS-064, com respostas novas.
- **Revelação antes do gatilho não tem categoria.** As cinco categorias não separam o paciente que conta uma omissão cedo demais (como no pi-09, A18, que obedeceu à instrução "[SISTEMA]"). Fica como sugestão para uma próxima versão das categorias.
