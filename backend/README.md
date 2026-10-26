# backend

API REST em FastAPI (Python). Reúne a integração com LLMs, o motor de cálculo determinístico e o acesso ao banco.

**Responsáveis:** Davi de Souza (API e LLM) e Mauro Barros (motor de cálculo e testes).

## Como rodar

Requer [uv](https://docs.astral.sh/uv/) e Python 3.11+. Os comandos rodam dentro de `backend/`.

```sh
uv sync                           # instala as dependências
cp .env.example .env              # preencha os valores
uv run --env-file .env fastapi dev   # sobe em http://localhost:8000
```

A documentação interativa da API (OpenAPI) fica em `http://localhost:8000/docs`.

| Variável | Uso | Padrão |
|---|---|---|
| `FRONTEND_URL` | origem do frontend liberada no CORS | `http://localhost:3000` |
| `DATABASE_URL` | conexão do PostgreSQL (string do Neon, `postgresql://...?sslmode=require`) | – |
| `GEMINI_API_KEY` | chave da API do Gemini ([Google AI Studio](https://aistudio.google.com/apikey)) | – |
| `LLM_MODELO` | modelo do Gemini usado pelo produto (por exemplo, `gemini-3.8-flash`); nunca fixado no código | – |
| `LLM_MODELO_JUIZ` | modelo do Gemini usado só pelo juiz do eval; precisa ser diferente de `LLM_MODELO` (ADR-005); nunca fixado no código | – |

## Contrato da API

O contrato com o frontend é o OpenAPI gerado pelo código (`/docs`). As rotas ficam sob `/api`. O `POST /api/sessoes` gera o caso com o LLM e salva a sessão no banco (NS-019). A fala do paciente continua fixa (mock) até a NS-020.

| Rota | Etapa | O que faz |
|---|---|---|
| `GET /api/perfis` | 1 | perfis e níveis de dificuldade |
| `POST /api/sessoes` | 1 | cria o caso e a sessão |
| `GET /api/sessoes/{id}` | 2 | estado e histórico, para retomar |
| `POST /api/sessoes/{id}/mensagens` | 2 | fala do paciente em SSE |
| `POST /api/sessoes/{id}/anamnese/encerrar` | 2 | encerra a anamnese e vai para o plano |
| `GET /api/alimentos?nome={termo}` | NS-013 | busca até 50 alimentos por nome, ignorando maiúsculas e acentos |

- **Streaming (SSE):** vários eventos `trecho` (`{"texto"}`), depois `fim` (`{"mensagem_id"}`) ou `erro` (`{"codigo", "mensagem"}`).
- **Erros:** toda resposta de erro tem o formato `{"erro": {"codigo", "mensagem"}}`. O frontend decide o que exibir pelo `codigo`.
- **Autenticação:** `Authorization: Bearer <token>` já está declarado, mas só passa a ser exigido na NS-035.

## Banco e migrações

O banco é PostgreSQL no Neon, com uma base para desenvolvimento e outra para produção. Cada pessoa usa a base de desenvolvimento no próprio `.env`, e a string de conexão nunca entra no commit. As migrações ficam em `app/db/migrations/` (Alembic).

```sh
uv run --env-file .env alembic upgrade head      # aplica as migrações pendentes
uv run --env-file .env alembic revision --autogenerate -m "descricao"   # depois de mudar app/db/modelos.py
uv run --env-file .env alembic downgrade -1      # desfaz a última
```

Revise o arquivo gerado antes do commit: o autogenerate não detecta tudo (por exemplo, renomear coluna vira apagar e criar).

Para testar sem o Neon, suba um Postgres local:

```sh
docker run -d --rm --name nutrisim-pg -e POSTGRES_PASSWORD=dev -e POSTGRES_DB=nutrisim -p 55432:5432 postgres:17-alpine
DATABASE_URL=postgresql://postgres:dev@localhost:55432/nutrisim uv run alembic upgrade head
```

Para importar ou atualizar a base TACO, execute a partir de `backend/`:

```sh
uv run --env-file .env python -m scripts.importar_taco
```

## Como testar

```sh
uv run pytest        # testes
uv run ruff check .  # lint (o mesmo da CI)
```

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

A versão é o nome do arquivo (`caso-v1.md`). Um prompt que já entrou na `desenvolvimento` não é editado: a mudança vira um arquivo novo (`caso-v2.md`) e o código passa a apontar para ele.

[`docs/prompts/`](../docs/prompts/README.md) é outra coisa: o **registro acadêmico** dos prompts que a equipe usou ao desenvolver o projeto com ajuda de IA.
