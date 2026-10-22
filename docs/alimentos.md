# Base de alimentos

Esta etapa adiciona ao NutriSim a base de composição de alimentos da TACO,
organizada no banco PostgreSQL e disponível para consulta pela API.

## Fonte dos dados

Os dados utilizados são da Tabela Brasileira de Composição de Alimentos
(TACO), 4ª edição, do NEPA/UNICAMP. Os arquivos CSV ficam em:

```text
backend/data/taco/
├── categories.csv
├── food.csv
├── nutrients.csv
└── fatty-acids.csv
```

Os arquivos representam:

- `categories.csv`: categorias dos alimentos;
- `food.csv`: identificação, nome e categoria de cada alimento;
- `nutrients.csv`: energia, macronutrientes e micronutrientes;
- `fatty-acids.csv`: gorduras e ácidos graxos, incluindo gordura saturada.

O campo `foodId` dos arquivos nutricionais e de ácidos graxos corresponde ao
campo `id` de `food.csv`.

## Modelagem do banco

As tabelas são declaradas em `backend/app/db/modelos.py`:

### `categorias`

Armazena os grupos alimentares.

```text
id
nome
```

### `alimentos`

Armazena a identificação dos alimentos.

```text
id
category_id -> categorias.id
nome
```

Uma categoria pode possuir vários alimentos:

```text
categorias 1 ──── N alimentos
```

### `nutrientes`

Armazena os valores nutricionais de cada alimento. O campo `id` é,
simultaneamente, chave primária e chave estrangeira para `alimentos.id`.

Essa estrutura representa uma relação um para um:

```text
alimentos 1 ──── 1 nutrientes
```

A tabela contém, entre outros:

- energia em kcal e kJ;
- proteína;
- lipídios;
- carboidratos;
- fibra alimentar;
- cálcio, magnésio, manganês, fósforo, ferro, sódio, potássio, cobre e zinco;
- retinol, equivalentes de retinol, equivalentes de atividade de retinol;
- tiamina, riboflavina, piridoxina, niacina e vitamina C.

### `acidos_graxos`

Armazena a composição de gorduras do alimento. Também possui relação um para
um com `alimentos`, usando `id` como chave primária e estrangeira.

Os campos principais são:

- `gordura_saturada`;
- `gordura_monoinsaturada`;
- `gordura_poliinsaturada`;
- ácidos graxos específicos, como láurico, palmítico, esteárico, oleico,
  linoleico, EPA, DHA e ácidos graxos trans.

A coluna `gordura_saturada` é a utilizada para a restrição de dislipidemia,
que limita a gordura saturada em relação ao valor energético total.

## Migrations

As migrations do Alembic criam a estrutura do banco de forma versionada e
reproduzível. A cadeia atual é:

```text
c06457c73871
    ↓
dd4596ebf3c4
    ↓
1a7c3e9b5d2f
    ↓
9f4a2b7c1d8e
```

As migrations relacionadas a esta etapa são:

- `1a7c3e9b5d2f`: cria `categorias`, `alimentos` e `nutrientes`;
- `9f4a2b7c1d8e`: cria `acidos_graxos`, depois de `alimentos`.

A chave `down_revision` garante que a tabela `alimentos` exista antes de
`acidos_graxos`, que possui uma chave estrangeira para ela.

Para aplicar a estrutura no banco:

```bash
cd backend
uv run --env-file .env alembic upgrade head
```

Para verificar a revisão instalada:

```bash
uv run --env-file .env alembic current
```

O banco deve indicar a revisão `9f4a2b7c1d8e (head)`.

## Script de importação

O script `backend/scripts/importar_taco.py` lê os quatro CSVs e alimenta as
tabelas na seguinte ordem:

```text
categorias → alimentos → nutrientes → acidos_graxos
```

Como o script importa módulos do pacote `app`, ele deve ser executado como
módulo Python:

```bash
cd backend
uv run --env-file .env python -m scripts.importar_taco
```

### Importação reproduzível

Os registros utilizam os identificadores da própria TACO como chaves
primárias. A importação usa upsert com `ON CONFLICT DO UPDATE`:

- registros novos são inseridos;
- registros existentes são atualizados;
- a execução repetida não cria duplicatas.

As quatro cargas são executadas dentro de uma única transação. Se uma etapa
falhar, a transação é revertida.

### Valores especiais da TACO

A função `converter_float` centraliza a conversão dos valores dos CSVs:

```text
valor numérico -> float
campo vazio    -> None
NA             -> None
Tr             -> 0.0
```

O valor `Tr` significa traço, ou seja, quantidade presente abaixo do limite de
detecção ou de quantificação da tabela. O valor `NA` significa dado não
disponível. Essa conversão permite armazenar os dados nos campos
`float | None` dos modelos.

## Verificação da carga

Depois da importação, as quantidades podem ser verificadas no SQL Editor do
Neon:

```sql
SELECT COUNT(*) AS categorias FROM categorias;
SELECT COUNT(*) AS alimentos FROM alimentos;
SELECT COUNT(*) AS nutrientes FROM nutrientes;
SELECT COUNT(*) AS acidos_graxos FROM acidos_graxos;
```

Na carga atual, os valores esperados são:

```text
categorias:    15
alimentos:    597
nutrientes:   597
acidos_graxos: 423
```

Nem todos os alimentos possuem registro de ácidos graxos, por isso a
quantidade de `acidos_graxos` pode ser menor que a quantidade de alimentos.

Uma consulta para validar as relações:

```sql
SELECT
    a.id,
    a.nome,
    c.nome AS categoria,
    n.kcal,
    n.proteina,
    n.fibra_alimentar,
    n.sodio,
    g.gordura_saturada
FROM alimentos AS a
JOIN categorias AS c ON c.id = a.category_id
JOIN nutrientes AS n ON n.id = a.id
LEFT JOIN acidos_graxos AS g ON g.id = a.id
ORDER BY a.id
LIMIT 10;
```

Para testar a idempotência, execute o importador novamente e repita as
contagens. Elas devem permanecer iguais:

```bash
uv run --env-file .env python -m scripts.importar_taco
```

## Endpoint de busca

A API disponibiliza:

```http
GET /api/alimentos?nome={termo}
```

Exemplo:

```bash
curl "http://localhost:8000/api/alimentos?nome=arroz"
```

O parâmetro `nome` é obrigatório, aceita entre 1 e 100 caracteres e a busca
retorna no máximo 50 alimentos.

A comparação ignora:

- letras maiúsculas e minúsculas;
- acentos;
- espaços no início e no fim do termo.

Assim, estas buscas são equivalentes:

```text
/api/alimentos?nome=arroz
/api/alimentos?nome=ARROZ
/api/alimentos?nome=árRoz
```

Resposta:

```json
[
  {
    "id": 1,
    "nome": "Arroz, integral, cozido",
    "categoria_id": 1,
    "kcal": 124.0,
    "proteina": 2.6,
    "carboidratos": 25.8,
    "lipidios": 1.0,
    "fibra_alimentar": 2.7,
    "sodio": 1.0,
    "gordura_saturada": 0.3
  }
]
```

Além da identificação e da categoria, a resposta traz os valores usados pelas
restrições atuais do motor: energia, proteína, carboidratos, lipídios, fibra
alimentar, sódio e gordura saturada. Os dados de `nutrientes` e
`acidos_graxos` são relacionados pelo mesmo código do alimento. Como alguns
alimentos não possuem registro de ácidos graxos, `gordura_saturada` pode ser
`null`.

A implementação está em:

```text
backend/app/api/alimentos.py
backend/app/schemas/alimentos.py
backend/app/db/deps.py
```

O endpoint normaliza o termo recebido com `unicodedata` e normaliza os nomes
armazenados na consulta PostgreSQL. A sessão do banco é fornecida por uma
dependência do FastAPI.

## Testes

Os testes da busca ficam em:

```text
backend/tests/test_alimentos.py
```

Eles verificam:

- remoção de acentos, maiúsculas e espaços;
- resposta do endpoint de busca.

Para executar os testes e o lint:

```bash
cd backend
uv run pytest
uv run ruff check .
```
