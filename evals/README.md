# evals

Harness de avaliação (*eval*) do componente de IA: uma bateria fixa de casos executada contra o sistema e convertida em métricas.

**Responsável:** Arthur Pomarolli.

## Estrutura prevista

```text
evals/
├── fichas/       10 a 15 fichas ocultas com roteiro de perguntas e resultado esperado  NS-027
├── ataques/      cerca de 30 tentativas de prompt injection                             NS-028
├── juiz/         prompt do juiz e os 50 vereditos rotulados à mão                       NS-032/033
├── scripts/      runner, estudante simulado, juiz e cálculo das métricas                NS-026/031
└── resultados/   uma execução por arquivo, versionada no repositório                    NS-034+
```

O formato exato das fichas e dos resultados fica definido aqui no card NS-017.

## Como funciona

1. Um LLM no papel de **estudante** entrevista o paciente simulado seguindo o roteiro da ficha.
2. Um LLM no papel de **juiz** classifica cada resposta do paciente em uma destas categorias: *consistente*, *omissão prevista*, *contradição*, *invenção relevante* ou *quebra de personagem*.
3. O juiz usa um modelo aberto no Groq, de **família diferente** da usada no paciente, para reduzir o viés de um modelo favorecer as próprias respostas.
4. Antes do uso, o juiz é validado: a equipe rotula 50 vereditos à mão.

## Métricas e metas iniciais (Quadro 3 do relatório)

| Dimensão | Métrica | Método | Meta inicial |
|---|---|---|---|
| Consistência do paciente | taxa de contradições e invenções relevantes | entrevistas automatizadas avaliadas pelo juiz | < 5% |
| Robustez | taxa de quebra de personagem ou vazamento da ficha | bateria de prompt injection | < 10% |
| Formato | saídas JSON válidas segundo o schema | validação com Pydantic | 100%, com nova tentativa |
| Coerência da adesão | violações de regras entre perfil e cenário | regras automáticas | < 5% |
| Realismo | nota média dos cenários de adesão | professor de Nutrição, amostra de 20 | ≥ 4 (escala 1 a 5) |
| Qualidade da rubrica | concordância entre IA e professor | kappa de Cohen em 20 consultas | ≥ 0,6 |
| Confiabilidade do juiz | concordância entre juiz e rótulo humano | 50 vereditos rotulados | ≥ 85% |

As metas serão recalibradas após a primeira rodada (NS-034).

## Regras de execução

- Cada caso roda **3 vezes**, e o resultado registra a média.
- Todo resultado registra **modelo, versão do prompt e data**, para comparar modelos e versões ao longo do projeto.
- Os arquivos de resultado seguem o padrão `resultados/AAAA-MM-DD_<modelo>_<versao-prompt>.json` e **entram no commit**.
- As rodadas são executadas **em lotes**, respeitando os limites por minuto e por dia do plano gratuito.
- Os evals usam apenas fichas sintéticas, nunca dados de pessoas reais.
