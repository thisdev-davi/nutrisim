# 2026-10-26 — Troca do juiz do eval do Groq pelo Gemini

- **Autor:** Arthur Pomarolli
- **Ferramenta e modelo:** Claude Code, com Claude Opus 5.5 (Anthropic)
- **Card:** NS-032
- **Tarefa:** levantar o que muda no projeto com a decisão de usar só o Gemini e atualizar a documentação que citava o Groq como provedor do juiz do eval.

## Prompt

Mensagens do autor, na ordem, copiadas sem alteração.

> Foi decidido em conjunto com o grupo que não seria usado mais o Groq para o aval do Juiz, confira os documentos referentes ao Groq e me mande eles, sera preciso fazer a alteração para o uso completo do Gemini

## Resultado

A IA procurou "Groq" no repositório e mostrou que nenhum código usava o provedor, só a documentação. Depois, propôs e aplicou as mudanças:

- `docs/decisoes.md`: nova ADR-005 (juiz do eval no Gemini, em modelo diferente do paciente, lido de `LLM_MODELO_JUIZ`), com o viés de autopreferência registrado como limitação e a cota gratuita dividida entre paciente, estudante simulado e juiz. A ADR-003 foi marcada como substituída em parte, sem apagar o texto original.
- `evals/README.md`, `README.md` e `docs/arquitetura.md`: Groq trocado por Gemini.
- `docs/kanban.md`: o NS-032 passou a se chamar "Criar o juiz do eval no Gemini".

O relatório da C1 e o documento do edital não foram alterados, porque já foram entregues ou são referência externa.

## Revisão humana

-  Foi feita a conferencia dos arquivos alterados e o registro antes do envio, ocorrendo a troca em 6 arquivos, ja que foi decidido com o grupo usar apenas o Gemini, conforme combinado.

