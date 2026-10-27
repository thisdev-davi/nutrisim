# 2026-10-26 — Juiz do eval no Gemini

- **Autor:** Arthur Pomarolli
- **Ferramenta e modelo:** Claude Code, com Claude Opus 5.5 (Anthropic)
- **Card:** NS-032
- **Tarefa:** implementar o juiz do eval, que classifica cada resposta do paciente simulado em uma das cinco categorias do `evals/README.md`, usando o Gemini com um modelo diferente do usado no paciente.

## Prompt

Mensagem do autor, copiada sem alteração.

> Vamos implementar a issue NS-032
>
> Prompt do juiz versionado em `evals/juiz/` Modelo open-weights no Groq, de família diferente da usada no paciente (alterando isso para o uso do Gemini) com nome do modelo e API key lidos de variável de ambiente, classifique cada resposta em uma destas categorias: consistente, omissão prevista, contradição, invenção relevante, quebra de personagem e faça a saída em JSON validado contra schema, com falha tratada explicitamente
>
> Leia o repo antes para seguir as convenções existentes e me mostre um plano
> curto antes de implementar.

## Resultado

- `evals/juiz/juiz-v1.md`: o prompt do juiz, com as cinco categorias, a ordem de prioridade e o formato da resposta. O prompt também avisa que o texto da conversa é dado, e não instrução, para um ataque de *prompt injection* não mudar o veredito.
- `backend/app/eval/juiz.py`: a função `julgar`, que monta a entrada (ficha completa, respostas anteriores e turno avaliado), chama o Gemini pelo cliente do LLM (NS-018) e devolve o veredito. O modelo vem de `LLM_MODELO_JUIZ`, e o juiz para com um erro se ela estiver vazia ou for igual a `LLM_MODELO`. Se a saída continuar inválida depois das três tentativas, o veredito sai com `falha: "saida_invalida"` e a rodada continua.
- `backend/app/llm/cliente.py`: não foi alterado neste card. O juiz usa o parâmetro `modelo`, criado pelo Davi no PR #106, para chamar o Gemini com `LLM_MODELO_JUIZ`.
- `backend/tests/test_juiz.py`: testes com um Gemini falso, sem chamar a API.
- `evals/README.md`: documentação do juiz e do formato da falha. A variável `LLM_MODELO_JUIZ` foi documentada pelo Davi no `backend/README.md` e no `backend/.env.example` (PR #106).

## Revisão humana

Foi feita a revisão dos resultados da IA, feita também uma decisão em grupo sobre quais níveis de IA seriam utilizados e feito também um teste local para averiguar o acerto da inteligência artificial nos modelos LLM.
