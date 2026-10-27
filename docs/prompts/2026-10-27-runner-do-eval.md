# 2026-10-27 — Runner do eval

- **Autor:** Arthur Pomarolli
- **Ferramenta e modelo:** Claude Code, com Claude Opus 5.5 (Anthropic)
- **Card:** NS-026
- **Tarefa:** criar o runner do harness de eval, que executa as fichas contra o paciente simulado, manda cada resposta ao juiz e salva o resultado, testado primeiro contra um paciente falso (respostas fixas) e, depois, ligado ao paciente real da NS-020.

## Prompt

Mensagem do autor, copiada sem alteração.

> Vamos criar o runner do harness de eval, script em evals/scripts/ que executa uma ficha contra o paciente simulado, o resultado salvo em evals/resultados/ com modelo, versão do prompt e data, execução em lotes, com pausa configurável para respeitar os limites do plano gratuito, decisão documentada: o runner chama a API ou importa os serviços do backend, desenvolvido contra um paciente falso (respostas fixas), sem esperar a NS-020 e uma ficha executada de ponta a ponta contra o paciente falso; a execução com o paciente real fica na NS-034

## Testes

Os testes foram feitos em duas etapas, no computador do autor (Windows), com a ficha `adulto-hipertensao-facil-01` (7 perguntas) e o juiz real no Gemini (`gemini-3.5-flash-lite`, prompt `juiz-v2`):

1. **Paciente falso:** primeiro, o runner rodou contra o paciente falso, que responde com frases fixas tiradas do roteiro e não chama o LLM. O objetivo era conferir o caminho completo (perguntas, juiz e arquivo de resultado) sem depender da NS-020. A rodada levou 31 segundos, sem nenhum veredito com falha. O juiz marcou como erro as duas respostas artificiais do paciente falso: "nada de diferente" diante da queixa principal (contradição) e a cópia literal do texto da ficha (quebra de personagem). Isso mostrou que o juiz está atento.
2. **Paciente real:** como a NS-020 foi mergeada durante o card, o runner foi ligado ao paciente simulado de verdade (`gemini-3.1-flash-lite`, prompt `paciente-v1`) e a mesma ficha rodou de novo. A rodada levou 1min36s, e as 7 respostas saíram consistentes. O paciente omitiu o hábito de beliscar na pergunta sobre o café da manhã, revelou o hábito diante da pergunta-gatilho e recusou informar o limite de sal sem sair do personagem.

Antes das duas rodadas, os testes automáticos do backend (150, com paciente e juiz falsos, sem chamar a API) e o lint passaram.

## Resultado

- `backend/app/eval/paciente.py`: a interface `Paciente` (o histórico e a pergunta entram, o texto da resposta sai), no mesmo formato da função `responder` do paciente real da NS-020, e o `PacienteFalso`, que responde com frases fixas tiradas do roteiro da ficha.
- `backend/app/eval/runner.py`: o runner. Faz as perguntas do roteiro, manda cada resposta ao juiz (NS-032), grava o resultado em `evals/resultados/AAAA-MM-DD_<modelo>_<versao-prompt>.json` depois de cada execução e retoma um lote interrompido sem repetir o que já rodou. Espera 15 s entre chamadas ao paciente e 5 s entre chamadas ao juiz (configurável) e, em erro de cota, espera e tenta de novo.
- `backend/app/eval/paciente.py` também tem o `PacienteReal`, que chama o paciente simulado da NS-020 direto (opção `--paciente real`).
- `backend/app/api/anamnese.py` e `backend/app/api/caso.py`: os prompts passam a ser lidos em UTF-8, porque no Windows os acentos saíam errados.
- `evals/scripts/rodar_eval.py`: o comando que roda o runner.
- `backend/tests/test_runner.py`: testes com paciente e juiz falsos, sem chamar a API.
- `evals/README.md`: como rodar e a decisão de importar os serviços do backend em vez de chamar a API.
- `evals/resultados/2026-10-27_paciente-falso_respostas-fixas-v1.json`: uma ficha (`adulto-hipertensao-facil-01`) executada de ponta a ponta no computador do autor, com o paciente falso e o juiz real no Gemini (`juiz-v2`). O juiz julgou as 7 respostas, sem falhas, e marcou como erro duas respostas artificiais do paciente falso (uma contradição e uma cópia literal da ficha).
- `evals/resultados/2026-10-27_gemini-3.1-flash-lite_paciente-v1.json`: a mesma ficha com o paciente real da NS-020 e o juiz real. As 7 respostas saíram consistentes, sem falhas.

## Revisão humana

Foram feitas revisões nos arquivos da IA. Também foi conferido e adicionado, ao longo do card, o teste feito com o paciente real da NS-020, apresentando resultados positivos em ambos os testes. Também foi corrigido um bug que poderia ocorrer em outros sistemas operacionais que não o Linux.
