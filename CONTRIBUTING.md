# Como contribuir

Toda mudança passa pela `desenvolvimento`, por pull request revisado por outro integrante, antes de chegar à `main`. Este guia vale para código e para documentação.

## Fluxo de trabalho

1. **Pegue um card** no quadro (GitHub Projects), atribua a si e mova-o para *Em andamento*.
2. **Crie uma branch** a partir da `desenvolvimento` atualizada:
   ```text
   <tipo>/NS-<id>-<descricao-curta>
   ```
   O tipo vem da tabela abaixo, o id é o do card e a descrição tem 2 a 4 palavras em minúsculas, separadas por hífen.
   Exemplos: `feat/NS-011-ci-configuration`, `feat/NS-020-paciente-simulado`, `docs/NS-007-contrato-api`.
3. **Faça commits** pequenos, cada um com um único contexto lógico.
4. **Abra o PR contra a `desenvolvimento`**, com o título no padrão das mensagens de commit (veja abaixo) e `Closes #<número da issue>` na descrição. O template de PR já traz as seções. Mova o card para *Em revisão*.
5. **Revisão:** outro integrante aprova e a CI fica verde. Só então o PR entra na `desenvolvimento` (squash merge). O título do PR vira a mensagem do commit.
6. Ao fechar a issue, o card vai sozinho para *Concluído*.
7. **Promoção para a `main`:** no fim de cada sprint e antes de cada entrega, um PR `desenvolvimento → main` leva o que foi validado. Esse PR usa *merge commit*, e não squash, para as duas branches continuarem com o mesmo histórico.

## Tipos de branch e de commit

| Tipo | Uso |
|---|---|
| `feat` | funcionalidade nova |
| `fix` | correção de bug |
| `test` | testes novos ou ajustados |
| `docs` | documentação |
| `refactor` | mudança interna sem alterar comportamento |
| `chore` | configuração, dependências, CI |

## Mensagens de commit

Vale para os commits e para o título dos PRs. Seguimos [Conventional Commits](https://www.conventionalcommits.org/pt-br/), em português, no imperativo e citando o card:

```text
<tipo>(<escopo>): <o que muda> (NS-<id>)
```

Exemplos:

```text
feat(motor): calcula GET por Mifflin-St Jeor (NS-024)
fix(llm): repete a chamada quando o JSON da ficha vem inválido (NS-018)
docs(api): descreve os endpoints da etapa de anamnese (NS-007)
```

Escopos usuais: `api`, `llm`, `motor`, `db`, `front`, `eval`, `content`, `docs`, `ci`.

## Definição de pronto para começar (Definition of Ready)

Um card só entra em *A fazer* quando tem:

- critérios de aceite verificáveis;
- responsável e milestone (sprint);
- dependências concluídas, ou um plano para contorná-las (por exemplo, mock do contrato da API).

## Definição de concluído (Definition of Done)

Um card só vai para *Concluído* quando:

- todos os critérios de aceite estão atendidos;
- o PR foi revisado e aprovado por outro integrante;
- a CI passou;
- a lógica nova tem teste (**obrigatório no motor de cálculo**);
- a documentação afetada foi atualizada (README da pasta, `docs/`);
- o uso de IA na tarefa, se houve, está registrado em [`docs/prompts/`](docs/prompts/README.md).

## Revisão de código

- Revise o comportamento, não só o estilo: rode localmente quando o PR mexe em fluxo.
- Confira as [regras de fronteira](docs/arquitetura.md#regras-de-fronteira) entre IA e motor.
- Comentários bloqueantes precisam dizer o que mudar. Sugestões opcionais começam com "opcional:".
- Prefira PRs pequenos. Um PR por card é a regra.

## Tamanho do PR

Um PR tem no máximo **500 linhas de lógica**, somando as adicionadas e as removidas em `backend/` e `frontend/`. Testes, lockfiles, docs, migrations e config não entram na conta. O check **Limite de 500 linhas** da CI reprova o PR que passar disso. Para conferir antes de abrir:

```sh
git diff --numstat origin/desenvolvimento...HEAD -- backend frontend \
  ':!*test*' ':!*.lock' ':!*lock.json' ':!*.md' ':!**/migrations/**' ':!*.toml' ':!*.json' \
  | awk '{s+=$1+$2} END {print s+0}'
```

Se passar, divida o card em PRs empilhados, cada um funcionando sozinho.

## Trabalho em paralelo com agentes

Vale para quem usa agentes de IA (Claude Code ou outro) em mais de um card ao mesmo tempo. É o mesmo fluxo de trabalho de antes, com quatro regras a mais.

1. **Um agente, um card, uma branch, um worktree.** Cada agente trabalha numa cópia própria do repositório, criada a partir da `desenvolvimento` atualizada:
   ```sh
   git fetch origin
   git worktree add ../nutrisim-NS-044 -b feat/NS-044-restricoes origin/desenvolvimento
   ```
   Ao terminar, rode `git worktree remove ../nutrisim-NS-044`.
2. **O contrato vem antes.** Os schemas em `backend/app/schemas/api.py`, as colunas em `backend/app/db/modelos.py` (com a migration) e o `docs/api.md` são a fronteira entre as trilhas e mudam **só em PR de contrato** (`docs(api): ...`), sem lógica. Esse PR entra antes de os agentes começarem. Se um agente precisar mudar o contrato, ele para e abre esse PR separado; os outros fazem rebase depois do merge.
3. **Cada trilha tem os seus arquivos.** O agente só edita os arquivos da trilha dele (veja a divisão da sprint em [`docs/sprints.md`](docs/sprints.md)). Nos arquivos compartilhados, a única mudança permitida é registrar a rota no `app/main.py` (uma linha).
4. **Briefing da trilha.** Quem dispara o agente cola no prompt:
   ```text
   Card: NS-<id> (#<issue>), critérios de aceite da issue
   Branch/worktree: <tipo>/NS-<id>-<descricao> em ../nutrisim-NS-<id>
   Pode editar: <arquivos da trilha>
   Só lê: app/schemas/api.py, app/db/modelos.py, docs/api.md
   Entrega: <função ou rota que a trilha expõe, com a assinatura do contrato>
   Consome: <o que vem de outra trilha; use mock se ainda não entrou>
   Pronto quando: gate abaixo verde e PR aberto contra a desenvolvimento
   ```

**Gate antes de pedir revisão humana**, rodado pelo próprio agente:

1. `uv run ruff check . && uv run pytest` no backend, ou `npm run lint && npm run test` no frontend;
2. a conta de linhas acima, com até 500;
3. `/ponytail-review` no diff, aplicando os cortes que fizerem sentido;
4. `/ecc:pr desenvolvimento --draft` para abrir o PR como rascunho;
5. `/ecc:review-pr` no rascunho, corrigindo o que for crítico ou importante;
6. `gh pr ready` e o card em *Em revisão*.

A CI repete as partes 1 e 2 em todo PR. A `desenvolvimento` só aceita merge com os checks verdes.

## Segredos e dados

- **Nunca faça commit de `.env`** nem de chaves de API. Use `.env.example` com os nomes das variáveis e sem valores.
- As chaves de LLM ficam **só no backend**. O frontend nunca chama o provedor de IA diretamente.
- Os casos clínicos são sintéticos. Não use dados de pacientes reais em fichas, testes ou evals.
- Os dados das sessões com estudantes são anonimizados antes de entrarem no repositório.

## Registro de uso de IA (exigência do edital)

Toda tarefa de engenharia de software feita com ajuda de IA (código, testes, documentação, relatórios) precisa ser registrada em `docs/prompts/`, com o prompt utilizado. O modelo de registro está em [`docs/prompts/README.md`](docs/prompts/README.md). O template de PR lembra desse passo.
