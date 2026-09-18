# backend

API REST em FastAPI (Python). Reúne a integração com LLMs, o motor de cálculo determinístico e o acesso ao banco.

**Responsáveis:** Davi de Souza (API e LLM) e Mauro Barros (motor de cálculo e testes).

> Ainda não há código. As instruções de instalação e execução entram com o card NS-008.

## Estrutura prevista

Cada pasta é criada pelo card indicado, junto com seu primeiro arquivo real:

```text
backend/
├── pyproject.toml          dependências e ferramentas (uv, pytest, ruff)            NS-008
├── .env.example            nomes das variáveis de ambiente, sem valores             NS-008
├── app/
│   ├── main.py             criação da aplicação e registro das rotas               NS-008
│   ├── config.py           leitura das variáveis (modelo LLM, chaves, banco)       NS-008
│   ├── api/                rotas REST agrupadas por etapa do fluxo                 NS-007/008
│   ├── schemas/            modelos Pydantic: contrato da API e ficha oculta        NS-014
│   ├── db/                 modelos do banco e migrações (Alembic)                  NS-012
│   ├── llm/                cliente do LLM, validação + nova tentativa,
│   │   │                   ferramentas (function calling), registro de tokens     NS-018
│   │   └── prompts/        prompts versionados do produto (caso, paciente,
│   │                       adesão, retorno, rubrica)                               NS-019+
│   ├── motor/              cálculo determinístico, SEM IA:
│   │                       composição, energia, adequação, restrições, projeção   NS-023+
│   └── services/           orquestração das 5 etapas (caso → retorno)
├── data/
│   └── taco/               TACO original (fonte NEPA/UNICAMP) + importação         NS-013
└── tests/
    ├── unit/               motor e schemas, comparados a contas feitas à mão       NS-029
    └── integration/        endpoints com o LLM substituído por respostas fixas     NS-030
```

## Regras desta pasta

- `motor/` não importa nada de `llm/`. O cálculo fisiológico nunca depende de IA.
- Toda saída estruturada do LLM é validada com Pydantic antes de ser usada.
- O prompt do paciente não recebe o gabarito da avaliação.
- O modelo de LLM é definido por variável de ambiente, nunca fixado no código.
- As chaves de API ficam só aqui, lidas do ambiente, e o `.env` nunca entra no commit.

Os detalhes estão em [`docs/arquitetura.md`](../docs/arquitetura.md#regras-de-fronteira).

## Prompts do produto × registro de uso de IA

`app/llm/prompts/` guarda os prompts **que o NutriSim usa em produção**. Eles são versionados porque o eval registra a versão de cada prompt.

[`docs/prompts/`](../docs/prompts/README.md) é outra coisa: o **registro acadêmico** dos prompts que a equipe usou ao desenvolver o projeto com ajuda de IA.
