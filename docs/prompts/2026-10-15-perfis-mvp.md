# 2026-10-15 — Perfis do MVP e níveis de dificuldade

- **Autor:** Arthur Pomarolli
- **Ferramenta e modelo:** Claude (app), com Claude Opus 5.5 (Anthropic)
- **Card:** NS-015
- **Tarefa:** propor os perfis de paciente do MVP, os níveis de dificuldade, as regras de diversidade e o caso de encaminhamento, e listar o que o schema da ficha (NS-014) precisa comportar.

## Contexto fornecido à IA

- Repositório `thisdev-davi/nutrisim`, branch `desenvolvimento`. A IA leu o relatório C1, `docs/arquitetura.md`, `docs/kanban.md`, `docs/caminho-critico.md`, `content/README.md`, `evals/README.md` e o contrato da API em `backend/app/schemas/api.py`.
- Captura de tela da issue #15 (NS-015) no GitHub, com os critérios de aceite.

## Prompt

O pedido foi feito com uma mensagem acompanhada da captura de tela da issue #15:

> ok, vamos começar por aqui, precisamos cumprir com o que pede no card

A captura de tela trazia os critérios de aceite do card, que definiram o que a IA devia produzir:

1. Lista de perfis do MVP (por exemplo, adulto com hipertensão), sem perfis pediátricos, de gestantes ou de atletas
2. Níveis de dificuldade descritos (por exemplo, quantidade de omissões e resistência do paciente)
3. Diversidade de renda, rotina e hábitos alimentares, revisada para evitar estereótipos
4. Um caso em que a conduta esperada é o encaminhamento
5. Schema da ficha oculta (NS-014) revisado à luz dos perfis definidos

O sexto critério da issue, o envio dos perfis para validação do professor de Nutrição, foi desconsiderado pelo autor durante a conversa.

Antes disso, o autor tinha enviado o link do repositório (`https://github.com/thisdev-davi/nutrisim`) para a IA ler o projeto.

## Resultado

- `content/perfis.md`: cinco perfis (hipertensão, diabetes tipo 2, dislipidemia, pessoa idosa com baixa ingestão e um caso de encaminhamento por sinais de transtorno alimentar), restrições verificáveis com referências, tabela dos três níveis de dificuldade, regras de diversidade com lista de conferência anti-estereótipo e campos necessários no schema da ficha.
- `content/README.md`: novo arquivo incluído na estrutura.

## Revisão humana

Na revisão humana foi revisado todo material entregue, ocorrendo algumas menores alterações de maneira manual nos documentos.
