# 2026-10-25 — Revisão do PR do motor de composição

- **Autor:** Mauro Barros
- **Ferramenta e modelo:** Claude Code, com Claude Opus 5.5 (Anthropic)
- **Card:** NS-023
- **Tarefa:** revisar o diff do PR #101 (motor de composição nutricional) e apontar as falhas, comprovando cada uma com testes antes de decidir o que corrigir.

## Prompt

Mensagens do autor, na ordem, copiadas sem alteração.

> /code-review revise o diff da minha branch atual para o PR que abri no github  https://github.com/thisdev-davi/nutrisim/pull/101

> Primeiro preciso que realize os testes para que eu possa avaliar se realmente o que sugeriu de alteracao faz sentido.

> Nao entendi o real problema do 2, me explique de forma detalhada.

## Resultado

A IA comparou o PR com a base `desenvolvimento`, conferiu as linhas de `backend/tests/composicao_contas.csv` com `backend/data/taco/nutrients.csv` (todas batem) e apontou 8 falhas em `backend/app/motor/composicao.py` e `backend/tests/test_composicao.py`. Depois, escreveu um script que reproduz cada falha no código do PR:

| # | Falha apontada | O que o teste mostrou |
|---|---|---|
| 1 | Porção NaN ou infinita passa pela validação | `gramas=nan` dá `kcal=nan` e `gramas=inf` dá `kcal=inf`, sem erro. O mesmo acontece com um nutriente NaN. |
| 2 | Chave de nutriente errada vira "dado faltante" | `{"fibra": 2.7}` em vez de `fibra_alimentar` soma 0 e lista o alimento em `sem_dado`, sem erro. |
| 3 | Alimento repetido em `sem_dado` no total do dia | Arroz no almoço e no jantar aparece duas vezes no aviso de vitamina C. |
| 4 | CSV do teste aberto sem `with` e sem encoding | Com `pytest -W error`, `test_bate_com_as_contas_a_mao[linha0]` falha com `PytestUnraisableExceptionWarning`. |
| 5 | Total do dia recalcula todos os itens | Não gera bug hoje, mas processa cada item duas vezes e o total pode deixar de bater com as refeições. |
| 6 | `frozen=True` com campos `dict` | `hash(item)` dá `TypeError` e `Resultado.valores` pode ser alterado. |
| 7 | `NUTRIENTES` repete à mão as colunas do ORM | Hoje todos os nomes existem em `Nutrientes`; o risco é só uma renomeação futura. |
| 8 | Erro de porção negativa não diz a refeição | `ValueError: Arroz: gramas=-1 negativa`, sem o nome da refeição. |

A IA explicou que a falha 2 depende de como o `Item` será montado a partir do banco: se o código ler as colunas usando a própria tupla `NUTRIENTES`, as chaves sempre estarão presentes e o problema não acontece.

## Revisão humana

- **O que o autor conferiu:** pediu que cada falha fosse comprovada com teste antes de aceitar a revisão, e questionou a falha 2 até entender o risco real.
- **O que o autor decidiu:**
  - aceitar as falhas 1, 3, 4 e 5 (a 5 como forma de resolver a 3);
  - manter o comportamento da falha 2, porque mudar o contrato obrigaria a reescrever os testes e o risco depende do código que ainda vai montar o `Item`;
  - deixar as falhas 6, 7 e 8 para depois, por não afetarem o uso atual.
