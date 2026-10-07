# Quadro de tarefas (kanban)

Este arquivo é a fonte dos cards do **GitHub Projects**. Cada card vira uma issue. As metas, os critérios de saída e os riscos de cada sprint estão em [`sprints.md`](sprints.md).

## Como montar o quadro no GitHub

### 1. Labels

Em *Issues → Labels → New label*:

| Label | Cor | Uso |
|---|---|---|
| `area:backend` | `#1D76DB` | API, serviços, banco |
| `area:frontend` | `#5319E7` | telas e experiência de uso |
| `area:llm` | `#D93F0B` | prompts, cliente do LLM, function calling |
| `area:motor` | `#0E8A16` | cálculo determinístico e TACO |
| `area:eval` | `#FBCA04` | harness de avaliação e métricas |
| `area:infra` | `#006B75` | CI, banco, deploy |
| `area:docs` | `#C5DEF5` | documentação e relatórios |
| `area:nutricao` | `#F9D0C4` | conteúdo e validação com o curso de Nutrição |
| `area:gestao` | `#BFD4F2` | organização, AVA, entregas |
| `tipo:feature` | `#A2EEEF` | funcionalidade do produto |
| `tipo:tarefa` | `#EDEDED` | configuração, definição, pesquisa |
| `tipo:teste` | `#C2E0C6` | testes automatizados e eval |
| `tipo:bug` | `#B60205` | algo quebrado |
| `tipo:entrega` | `#FEF2C0` | entregável de checkpoint (C1, C2, C3) |
| `bloqueado` | `#E11D21` | card parado por dependência externa |

### 2. Milestones (sprints)

Em *Issues → Milestones → New milestone*. Os títulos precisam ser exatamente estes, porque os cards os citam:

| Milestone | Vencimento | Descrição |
|---|---|---|
| Sprint 0 — C1 | 18/09/2026 | Entregar a C1 com o repositório organizado |
| Sprint 1 — Fundação | 04/10/2026 | Base pronta para trabalho em paralelo |
| Sprint 2 — Paciente e motor | 18/10/2026 | Conversa com o paciente gerado e motor calculando |
| Sprint 3 — Protótipo (C2) | 30/10/2026 | IA funcionando, primeiros testes e eval |
| Sprint 4 — Plano e cenários | 15/11/2026 | Etapas 3 e 4 funcionando |
| Sprint 5 — Retorno e rubrica | 22/11/2026 | Fluxo completo, da etapa 1 à 5 |
| Sprint 6 — Deploy e sessões | 29/11/2026 | MVP público e indicadores coletados |
| Sprint 7 — MVP (C3) | 04/12/2026 | Entregar a C3 |

### 3. Project

Em *Projects → New project → Board*:

1. **Colunas (campo Status):** `Backlog`, `A fazer`, `Em andamento`, `Em revisão`, `Concluído`.
2. **Workflows** (menu `⋯` → *Workflows*):
   - *Auto-add to project* com o filtro `is:issue`;
   - *Item added to project*: `Backlog`;
   - *Item closed* e *Pull request merged*: `Concluído`.
3. **Campo Prioridade:** em *Settings → Custom fields*, crie o campo *Prioridade* (single select) com `P0`, `P1`, `P2` e `P3`, e preencha com o valor de cada card.
4. **Visões:**
   - *Quadro*: board filtrado pela sprint atual, por exemplo `milestone:"Sprint 1 — Fundação"`;
   - *Por pessoa*: tabela agrupada por *Assignees*;
   - *Sprints*: tabela agrupada por *Milestone*;
   - *Caminho crítico*: tabela filtrada por `Prioridade: P0`, ordenada por *Milestone*.
5. Vincule o project ao repositório (*Settings → Manage access*) para que o professor também o veja.

### 4. Cards

Para cada card abaixo, abra *New issue → Tarefa* e siga estes passos:
1. O **título** é a linha do card sem o `### `, por exemplo `NS-020 — Implementar o paciente simulado com streaming`.
2. O **corpo** é tudo o que vem abaixo do título, até o próximo card.
3. Aplique as **labels** e o **milestone** indicados. Em **responsável**, use o usuário GitHub do integrante.

O prefixo `NS-xxx` fica no título para que o campo "Depende de" continue rastreável depois da importação.

## Legenda

- **Responsável:** cada card tem um único dono, que responde pelo card no quadro. Entre parênteses, quem apoia. Os papéis mudaram depois da C1: **Pedro assumiu o frontend e Arthur assumiu o eval e a governança de IA** (ver [Divisão por integrante](#divisão-por-integrante)).
- **Prioridade:** o detalhe está em [`caminho-critico.md`](caminho-critico.md).
  - **P0:** está no caminho crítico; um dia de atraso atrasa a C2 ou a C3;
  - **P1:** bloqueia outro card, mas tem folga;
  - **P2:** não bloqueia nenhum card; pode escorregar dentro da sprint;
  - **P3:** desejável, só entra com folga.
- **Bloqueia:** cards que só começam quando este terminar. É o inverso do "Depende de".
- **Tamanho:**
  - **P:** até meio dia;
  - **M:** 1 a 2 dias;
  - **G:** 3 dias ou mais. Nesse caso, vale dividir o card.
- **RF:** requisito funcional do Quadro 1 do relatório.
- **Pronto:** segue a definição de concluído do [`CONTRIBUTING.md`](../CONTRIBUTING.md#definição-de-concluído-definition-of-done).

## Divisão por integrante

Carga estimada com P = 0,5, M = 1,5 e G = 3 dias. O backlog (NS-069) fica fora da conta.

| Integrante | Papel | Cards | Carga | P0 |
|---|---|---|---|---|
| Arthur Pomarolli | Eval, métricas, governança de IA e contato com a Nutrição | 19 | ~28,5 dias | 10 |
| Davi de Souza | Backend, integração com LLMs e testes | 16 | ~26,5 dias | 8 |
| Pedro Augusto | Frontend responsivo e experiência de uso | 14 | ~24,5 dias | 3 |
| Mauro Barros | Motor de cálculo, backend, testes e entregas no AVA | 19 | ~25 dias | 6 |

| Sprint | Arthur | Davi | Pedro | Mauro |
|---|---|---|---|---|
| 0 — C1 | NS-004 | NS-001, NS-002 | NS-005 | NS-003, NS-006 |
| 1 — Fundação | NS-015, NS-016, NS-017 | NS-007, NS-008, NS-014 | NS-009, NS-010 | NS-011, NS-012, NS-013 |
| 2 — Paciente e motor | NS-026, NS-027, NS-028 | NS-019, NS-020, NS-024 | NS-021, NS-022 | NS-018, NS-023, NS-025 |
| 3 — Protótipo (C2) | NS-031, NS-032, NS-033, NS-034 | NS-030, NS-035 | NS-036, NS-037, NS-039 | NS-029, NS-038, NS-040 |
| 4 — Plano e cenários | NS-047, NS-049 | NS-044, NS-046 | NS-042, NS-048 | NS-041, NS-043, NS-045 |
| 5 — Retorno e rubrica | NS-056, NS-057 | NS-051, NS-055 | NS-052, NS-054 | NS-050, NS-053 |
| 6 — Deploy e sessões | NS-062, NS-063 | NS-058, NS-060 | NS-061 | NS-059 |
| 7 — MVP (C3) | NS-064, NS-065 | – | NS-067 | NS-066, NS-068 |
| Backlog | – | – | NS-069 | – |

Da Sprint 2 em diante, Davi e Mauro dividem o backend e os testes: cada um implementa funções do backend e do motor e escreve testes, sem separar "quem codifica" de "quem testa".

Autoavaliação, avaliação 360° e inscrição no AVA continuam sendo feitas por cada integrante; o dono do card só garante que todos fizeram.

---

## Sprint 0 — C1 (até 18/09)

### NS-001 — Criar o repositório no GitHub e publicar a estrutura inicial
`area:infra` `tipo:entrega` · **Milestone:** Sprint 0 — C1 · **Responsável:** Davi · **Prioridade:** P0 · **Tamanho:** P · **Depende de:** – · **Bloqueia:** NS-002, NS-003

Publicar esta estrutura de pastas e documentação, que o edital pede como "GitHub inicial" na C1.

- [x] Repositório `nutrisim` criado e conteúdo publicado na `main`
- [x] Integrantes adicionados com permissão de escrita
- [ ] Professor (howard.cruz@faesa.br) adicionado como colaborador
- [ ] `main` protegida: PR obrigatório, 1 aprovação, sem push direto. Em repositório privado, isso exige o GitHub Pro, que é gratuito no GitHub Student Developer Pack
- [ ] Descrição e tópicos do repositório preenchidos

### NS-002 — Montar o quadro no GitHub Projects e importar os cards
`area:gestao` `tipo:tarefa` · **Milestone:** Sprint 0 — C1 · **Responsável:** Davi · **Prioridade:** P2 · **Tamanho:** M · **Depende de:** NS-001 · **Bloqueia:** –

- [ ] Labels e milestones criados conforme o início deste arquivo
- [ ] Project com as 5 colunas e os workflows automáticos ativos
- [ ] Cards importados como issues, com labels, milestone e responsável
- [ ] Project vinculado ao repositório e visível para o professor
- [ ] Cards das Sprints 0 e 1 em `A fazer`; os demais em `Backlog`

### NS-003 — Preencher os destaques pendentes do relatório e gerar a versão final
`area:docs` `tipo:entrega` · **Milestone:** Sprint 0 — C1 · **Responsável:** Mauro · **Prioridade:** P0 · **Tamanho:** P · **Depende de:** NS-001 · **Bloqueia:** NS-006

O relatório ainda tem trechos marcados com `==destaque==`.

- [ ] URL real do repositório na seção 6.3
- [ ] Meta de alcance do Quadro 4 definida (proposta atual: ao menos 15 estudantes)
- [ ] Nenhum `==destaque==` restante, e o aviso sobre os destaques no início do relatório removido
- [ ] Versão final exportada no formato exigido pelo AVA e salva em `docs/relatorios/`

### NS-004 — Registrar em docs/prompts os prompts usados na elaboração do relatório
`area:docs` `tipo:tarefa` · **Milestone:** Sprint 0 — C1 · **Responsável:** Arthur · **Prioridade:** P0 · **Tamanho:** P · **Depende de:** – · **Bloqueia:** NS-006

O edital exige que todo uso de IA na engenharia de software seja registrado com o prompt.

- [ ] Um arquivo por tarefa em `docs/prompts/`, seguindo o modelo do README da pasta
- [ ] Prompts literais, com a ferramenta ou modelo e o que foi aproveitado
- [ ] Revisão humana descrita: o que a equipe conferiu ou alterou

### NS-005 — Informar a composição do grupo ao professor e se inscrever no AVA
`area:gestao` `tipo:entrega` · **Milestone:** Sprint 0 — C1 · **Responsável:** Pedro · **Prioridade:** P2 · **Tamanho:** P · **Depende de:** – · **Bloqueia:** –

- [ ] E-mail enviado a howard.cruz@faesa.br com os 4 integrantes e o tema
- [ ] Todos inscritos no grupo correspondente no AVA

### NS-006 — Entregar a C1 e fazer a autoavaliação e a avaliação 360°
`area:gestao` `tipo:entrega` · **Milestone:** Sprint 0 — C1 · **Responsável:** Mauro · **Prioridade:** P0 · **Tamanho:** P · **Depende de:** NS-003, NS-004 · **Bloqueia:** –

- [ ] Relatório e link do repositório enviados no "Envio de Trabalho" da C1
- [ ] Autoavaliação preenchida por cada integrante
- [ ] Avaliação 360° entre pares preenchida (modelo do Quadro de Avaliações)

---

## Sprint 1 — Fundação (21/09 a 04/10)

### NS-007 — Definir o contrato da API REST
`area:backend` `area:frontend` `tipo:tarefa` · **Milestone:** Sprint 1 — Fundação · **Responsável:** Davi (apoio: Pedro) · **Prioridade:** P1 · **Tamanho:** M · **Depende de:** – · **Bloqueia:** NS-021, NS-022

Sem contrato, front e back travam um ao outro. Esse é um risco listado no Quadro 7 do relatório.

- [ ] `docs/api.md` com os endpoints das 5 etapas: método, rota, corpo, resposta e erros
- [ ] Formato do streaming do paciente definido (por exemplo, Server-Sent Events)
- [ ] Autenticação e formato de erro padronizados
- [ ] Nenhum endpoint devolve a ficha oculta ao frontend
- [ ] Contrato aprovado pelos quatro integrantes no PR

### NS-008 — Configurar o backend
`area:backend` `area:infra` `tipo:tarefa` · **Milestone:** Sprint 1 — Fundação · **Responsável:** Davi · **Prioridade:** P0 · **Tamanho:** M · **Depende de:** – · **Bloqueia:** NS-011, NS-012, NS-018

- [ ] Projeto FastAPI com a estrutura do `backend/README.md` e dependências no `pyproject.toml` (uv)
- [ ] Configuração lida de variáveis de ambiente, com um `.env.example` sem valores (chaves, `DATABASE_URL`, nomes dos modelos)
- [ ] `GET /health` respondendo
- [ ] pytest e ruff configurados, com um teste de exemplo passando
- [ ] README do backend explicando como instalar, rodar e testar

### NS-009 — Configurar o frontend
`area:frontend` `area:infra` `tipo:tarefa` · **Milestone:** Sprint 1 — Fundação · **Responsável:** Pedro · **Prioridade:** P1 · **Tamanho:** M · **Depende de:** – · **Bloqueia:** NS-011, NS-021

- [ ] Projeto Next.js + Tailwind em `frontend/`. O `create-next-app` exige pasta vazia, então o README sai antes e volta depois
- [ ] Layout base mobile-first, sem rolagem horizontal a partir de 360 px
- [ ] Lint configurado e passando
- [ ] URL da API lida de variável de ambiente
- [ ] README do frontend explicando como instalar e rodar

### NS-010 — Desenhar os wireframes das 5 etapas no celular
`area:frontend` `tipo:tarefa` · **Milestone:** Sprint 1 — Fundação · **Responsável:** Pedro · **Prioridade:** P1 · **Tamanho:** M · **Depende de:** – · **Bloqueia:** NS-021, NS-022

- [ ] Telas: início, login, escolha do caso, anamnese, plano, cenários, retorno, feedback e histórico
- [ ] Versão para celular (360 px) e adaptação das telas principais para desktop
- [ ] Imagens ou link (por exemplo, Figma) salvos em `docs/wireframes/`
- [ ] Revisados pela equipe antes das telas da Sprint 2

### NS-011 — Configurar a CI no GitHub Actions
`area:infra` `tipo:teste` · **Milestone:** Sprint 1 — Fundação · **Responsável:** Mauro · **Prioridade:** P1 · **Tamanho:** M · **Depende de:** NS-008, NS-009 · **Bloqueia:** NS-038

- [ ] Workflow em `.github/workflows/` rodando lint e testes do backend e do frontend em todo PR
- [ ] Checagens marcadas como obrigatórias para o merge na `main`
- [ ] Nenhuma chave real usada na CI; os testes usam o LLM mockado
- [ ] CI terminando em menos de 10 minutos

### NS-012 — Provisionar o PostgreSQL no Neon com migrações
`area:infra` `area:backend` `tipo:tarefa` · **Milestone:** Sprint 1 — Fundação · **Responsável:** Mauro · **Prioridade:** P1 · **Tamanho:** P · **Depende de:** NS-008 · **Bloqueia:** NS-013

- [ ] Banco criado no Neon (plano gratuito), com bases separadas para desenvolvimento e produção
- [ ] Alembic configurado e a primeira migração aplicada
- [ ] `DATABASE_URL` documentada no `.env.example`, sem credenciais no repositório
- [ ] Instruções de migração no README do backend

### NS-013 — Importar a TACO e expor a busca de alimentos
`area:motor` `area:backend` `tipo:feature` · **Milestone:** Sprint 1 — Fundação · **Responsável:** Mauro · **Prioridade:** P1 · **Tamanho:** M · **RF:** RF05 · **Depende de:** NS-012 · **Bloqueia:** NS-023, NS-046

- [ ] Fonte oficial (TACO, 4ª ed., NEPA/UNICAMP) citada em `backend/data/taco/`
- [ ] Script de importação reproduzível: rodar de novo não duplica dados
- [ ] Tabela de alimentos com energia, macronutrientes e os micronutrientes usados pelo motor (por exemplo, sódio, fibra, cálcio, ferro)
- [ ] Tratamento documentado dos valores "Tr" (traço) e "NA" da TACO
- [ ] Busca por nome que ignora acentos e maiúsculas, com endpoint e teste

### NS-014 — Definir o schema da ficha oculta
`area:backend` `area:llm` `tipo:tarefa` · **Milestone:** Sprint 1 — Fundação · **Responsável:** Davi · **Prioridade:** P0 · **Tamanho:** M · **RF:** RF03 · **Depende de:** NS-015 · **Bloqueia:** NS-019, NS-027

- [ ] Modelo Pydantic e JSON Schema cobrindo:
  - dados antropométricos;
  - rotina, preferências e aversões;
  - orçamento;
  - restrições (por exemplo, limite de sódio);
  - informações que o paciente omite, cada uma com o gatilho que a revela
- [ ] Separação explícita entre o que o paciente sabe e o gabarito da avaliação
- [ ] Um exemplo completo validado pelo schema
- [ ] Revisado por Arthur (eval) e por Mauro (motor)

### NS-015 — Definir os perfis do MVP e os níveis de dificuldade
`area:nutricao` `tipo:tarefa` · **Milestone:** Sprint 1 — Fundação · **Responsável:** Arthur · **Prioridade:** P0 · **Tamanho:** M · **Depende de:** – · **Bloqueia:** NS-014

- [ ] Lista de perfis do MVP (por exemplo, adulto com hipertensão), sem perfis pediátricos, de gestantes ou de atletas
- [ ] Níveis de dificuldade descritos (por exemplo, quantidade de omissões e resistência do paciente)
- [ ] Diversidade de renda, rotina e hábitos alimentares, revisada para evitar estereótipos
- [ ] Um caso em que a conduta esperada é o encaminhamento (por exemplo, sinais de transtorno alimentar)
- [ ] Perfis enviados para validação do professor de Nutrição (NS-016)

### NS-016 — Fazer o contato com o curso de Nutrição
`area:nutricao` `area:gestao` `tipo:tarefa` · **Milestone:** Sprint 1 — Fundação · **Responsável:** Arthur · **Prioridade:** P0 · **Tamanho:** P · **Depende de:** – · **Bloqueia:** NS-049

- [ ] Projeto apresentado à coordenação ou a um professor do curso
- [ ] Professor de referência definido para validar perfis, limites das restrições, rubrica e cenários
- [ ] Sessões com estudantes pré-agendadas para a Sprint 6 (até 30 min cada) e meta de alcance combinada
- [ ] Confirmado com o professor da disciplina se as sessões dispensam apreciação do CEP (ver a Res. CNS 510/2016, art. 1º, parágrafo único)

### NS-017 — Definir o formato das fichas de eval e das métricas
`area:eval` `tipo:tarefa` · **Milestone:** Sprint 1 — Fundação · **Responsável:** Arthur · **Prioridade:** P1 · **Tamanho:** P · **Depende de:** – · **Bloqueia:** NS-026, NS-027, NS-032

- [ ] Formato das fichas de eval (ficha oculta, roteiro de perguntas e resultado esperado) documentado em `evals/README.md`
- [ ] Definição operacional de cada categoria do juiz, com um exemplo de cada
- [ ] Formato dos arquivos de resultado: modelo, versão do prompt, data e métricas
- [ ] Fórmula de cada métrica do Quadro 3

---

## Sprint 2 — Paciente e motor (05/10 a 18/10)

### NS-018 — Implementar o cliente do LLM com saída estruturada e registro de tokens
`area:llm` `area:backend` `tipo:feature` · **Milestone:** Sprint 2 — Paciente e motor · **Responsável:** Mauro · **Prioridade:** P0 · **Tamanho:** M · **Depende de:** NS-008 · **Bloqueia:** NS-019, NS-046

Base comum para as cinco tarefas de IA do produto.

- [ ] Cliente do Gemini Flash com o nome do modelo lido de variável de ambiente
- [ ] Saída estruturada por JSON schema, validada com Pydantic
- [ ] Nova tentativa automática quando a saída vem inválida, com limite de tentativas e erro claro quando elas se esgotam
- [ ] Tokens de entrada e saída registrados por chamada e associados à sessão
- [ ] Testes com o provedor mockado, sem chamadas reais na CI

### NS-019 — Gerar o caso com ficha oculta
`area:llm` `area:backend` `tipo:feature` · **Milestone:** Sprint 2 — Paciente e motor · **Responsável:** Davi · **Prioridade:** P0 · **Tamanho:** M · **RF:** RF02, RF03 · **Depende de:** NS-014, NS-018 · **Bloqueia:** NS-020, NS-030

- [ ] Prompt de geração versionado em `backend/app/llm/prompts/`
- [ ] Endpoint que recebe perfil e dificuldade e cria o caso e a sessão
- [ ] Ficha gerada validada pelo schema da NS-014 antes de ser salva
- [ ] Resposta ao frontend sem a ficha oculta, só com o que o estudante pode ver (por exemplo, nome e queixa principal)
- [ ] Teste de integração com LLM mockado

### NS-020 — Implementar o paciente simulado com streaming
`area:llm` `area:backend` `tipo:feature` · **Milestone:** Sprint 2 — Paciente e motor · **Responsável:** Davi · **Prioridade:** P0 · **Tamanho:** G · **RF:** RF04 · **Depende de:** NS-019 · **Bloqueia:** NS-026, NS-030

O paciente responde só com o que conheceria: hábitos, sintomas, rotina e preferências. As omissões só aparecem diante de perguntas adequadas.

- [ ] Prompt do paciente versionado, sem o gabarito da avaliação
- [ ] Regras de omissão da ficha aplicadas: a informação só aparece diante do gatilho
- [ ] Resposta em streaming, com início em até 3 s medido em condições normais de uso
- [ ] Histórico da conversa salvo por sessão e reenviado a cada turno
- [ ] Instruções contra quebra de personagem e vazamento da ficha

### NS-021 — Criar a tela de seleção de perfil e dificuldade
`area:frontend` `tipo:feature` · **Milestone:** Sprint 2 — Paciente e motor · **Responsável:** Pedro · **Prioridade:** P1 · **Tamanho:** M · **RF:** RF02 · **Depende de:** NS-007, NS-009, NS-010 · **Bloqueia:** NS-037

- [ ] Perfis e níveis de dificuldade vindos da API (ou do mock do contrato)
- [ ] Ao confirmar, cria o caso e leva à anamnese
- [ ] Estado de carregamento durante a geração do caso e erro com opção de tentar de novo
- [ ] Utilizável a partir de 360 px e por teclado

### NS-022 — Criar a tela de chat da anamnese
`area:frontend` `tipo:feature` · **Milestone:** Sprint 2 — Paciente e motor · **Responsável:** Pedro · **Prioridade:** P1 · **Tamanho:** G · **RF:** RF04 · **Depende de:** NS-007, NS-010 · **Bloqueia:** NS-037

- [ ] Mensagens do paciente exibidas em streaming, conforme o contrato
- [ ] Histórico visível e preservado ao recarregar a página
- [ ] Campo de mensagem acessível: rótulo, envio por teclado, foco gerenciado
- [ ] Novas mensagens anunciadas a leitores de tela (região `aria-live`)
- [ ] Botão para encerrar a anamnese e seguir para o plano

### NS-023 — Motor: calcular a composição nutricional
`area:motor` `tipo:feature` · **Milestone:** Sprint 2 — Paciente e motor · **Responsável:** Mauro · **Prioridade:** P1 · **Tamanho:** M · **RF:** RF05 · **Depende de:** NS-013 · **Bloqueia:** NS-025, NS-029, NS-041

- [ ] Função pura que recebe alimentos da TACO com porções em gramas e devolve o total e o valor por refeição
- [ ] Energia, carboidratos, proteínas, lipídios, fibras e os micronutrientes selecionados
- [ ] Nenhuma dependência de `llm/`
- [ ] Testes com valores conferidos à mão

### NS-024 — Motor: calcular a necessidade energética (GET)
`area:motor` `tipo:feature` · **Milestone:** Sprint 2 — Paciente e motor · **Responsável:** Davi · **Prioridade:** P1 · **Tamanho:** P · **RF:** RF05 · **Depende de:** – · **Bloqueia:** NS-029, NS-045

- [ ] Taxa metabólica basal por Mifflin-St Jeor (MIFFLIN et al., 1990), para os dois sexos
- [ ] GET = TMB × fator de atividade, com os fatores e a fonte documentados
- [ ] Entradas validadas (idade, peso e altura em faixas plausíveis)
- [ ] Testes com valores conferidos à mão

### NS-025 — Motor: calcular a adequação de nutrientes às DRIs
`area:motor` `tipo:feature` · **Milestone:** Sprint 2 — Paciente e motor · **Responsável:** Mauro · **Prioridade:** P1 · **Tamanho:** M · **RF:** RF08 · **Depende de:** NS-023 · **Bloqueia:** NS-029

- [ ] Valores de referência das DRIs (INSTITUTE OF MEDICINE, 2006) para os nutrientes selecionados, por sexo e faixa etária, com a fonte citada
- [ ] Percentual de adequação de cada nutriente em relação à referência
- [ ] Classificação simples (abaixo, adequado, acima), com os limites documentados
- [ ] Testes com valores conferidos à mão

### NS-026 — Criar o runner do harness de eval
`area:eval` `tipo:teste` · **Milestone:** Sprint 2 — Paciente e motor · **Responsável:** Arthur · **Prioridade:** P0 · **Tamanho:** M · **Depende de:** NS-017, NS-020 · **Bloqueia:** NS-031

- [ ] Script em `evals/scripts/` que executa uma ficha contra o paciente simulado
- [ ] Resultado salvo em `evals/resultados/` com modelo, versão do prompt e data
- [ ] Execução em lotes, com pausa configurável para respeitar os limites do plano gratuito
- [ ] Decisão documentada: o runner chama a API ou importa os serviços do backend
- [ ] Uma ficha executada de ponta a ponta

### NS-027 — Escrever as fichas de eval
`area:eval` `area:nutricao` `tipo:teste` · **Milestone:** Sprint 2 — Paciente e motor · **Responsável:** Arthur · **Prioridade:** P1 · **Tamanho:** G · **Depende de:** NS-014, NS-017 · **Bloqueia:** NS-034

- [ ] De 10 a 15 fichas cobrindo os perfis e níveis do MVP
- [ ] Cada ficha com roteiro de perguntas e resultado esperado: o que deve ser revelado, omitido ou recusado
- [ ] Fichas validadas pelo schema da NS-014
- [ ] Pelo menos uma ficha com caso de encaminhamento

### NS-028 — Montar a bateria de prompt injection
`area:eval` `tipo:teste` · **Milestone:** Sprint 2 — Paciente e motor · **Responsável:** Arthur · **Prioridade:** P1 · **Tamanho:** M · **Depende de:** – · **Bloqueia:** NS-034

- [ ] Cerca de 30 tentativas em `evals/ataques/`, cobrindo:
  - pedir a ficha ou o gabarito;
  - mandar sair do personagem;
  - esconder instruções na mensagem;
  - pedir diagnóstico ou prescrição
- [ ] Resultado esperado de cada ataque: o paciente se mantém no personagem e não vaza a ficha
- [ ] Referência às categorias do OWASP Top 10 for LLM Applications (2025)

---

## Sprint 3 — Protótipo (C2) (19/10 a 30/10)

### NS-029 — Escrever os testes unitários do motor
`area:motor` `tipo:teste` · **Milestone:** Sprint 3 — Protótipo (C2) · **Responsável:** Mauro · **Prioridade:** P2 · **Tamanho:** M · **Depende de:** NS-023, NS-024, NS-025 · **Bloqueia:** –

- [ ] Composição, GET e adequação comparados a contas feitas à mão, com a planilha das contas salva junto aos testes
- [ ] Casos-limite: porção zero, alimento com "Tr" ou "NA", entradas fora da faixa
- [ ] Rodando na CI

### NS-030 — Escrever os testes de integração da API
`area:backend` `tipo:teste` · **Milestone:** Sprint 3 — Protótipo (C2) · **Responsável:** Davi · **Prioridade:** P2 · **Tamanho:** M · **Depende de:** NS-019, NS-020 · **Bloqueia:** –

- [ ] Endpoints de caso, anamnese e busca na TACO testados
- [ ] LLM substituído por respostas fixas, com resultados reproduzíveis
- [ ] Teste garantindo que a ficha oculta nunca aparece nas respostas da API
- [ ] Rodando na CI

### NS-031 — Criar o estudante simulado
`area:eval` `area:llm` `tipo:teste` · **Milestone:** Sprint 3 — Protótipo (C2) · **Responsável:** Arthur · **Prioridade:** P0 · **Tamanho:** M · **Depende de:** NS-026 · **Bloqueia:** NS-034

- [ ] LLM no papel de estudante, conduzindo a entrevista a partir do roteiro da ficha
- [ ] Conversa completa salva junto ao resultado
- [ ] Número de turnos limitado, para controlar o custo

### NS-032 — Criar o juiz do eval no Groq
`area:eval` `area:llm` `tipo:teste` · **Milestone:** Sprint 3 — Protótipo (C2) · **Responsável:** Arthur · **Prioridade:** P1 · **Tamanho:** M · **Depende de:** NS-017 · **Bloqueia:** NS-033

- [ ] Prompt do juiz versionado em `evals/juiz/`
- [ ] Modelo aberto no Groq, de família diferente da usada no paciente, lido de variável de ambiente
- [ ] Cada resposta classificada como consistente, omissão prevista, contradição, invenção relevante ou quebra de personagem
- [ ] Saída do juiz em JSON validado

### NS-033 — Validar o juiz com vereditos rotulados à mão
`area:eval` `tipo:teste` · **Milestone:** Sprint 3 — Protótipo (C2) · **Responsável:** Arthur (os quatro rotulam) · **Prioridade:** P1 · **Tamanho:** M · **Depende de:** NS-032 · **Bloqueia:** NS-034

- [ ] Amostra de 50 vereditos rotulada pela equipe sem ver a classificação do juiz
- [ ] Taxa de acerto do juiz calculada (meta: pelo menos 85%)
- [ ] Se ficar abaixo da meta, prompt do juiz ajustado e acerto medido de novo
- [ ] Rótulos e resultado salvos em `evals/juiz/`

### NS-034 — Executar a primeira rodada de eval
`area:eval` `tipo:teste` · **Milestone:** Sprint 3 — Protótipo (C2) · **Responsável:** Arthur · **Prioridade:** P0 · **Tamanho:** M · **Depende de:** NS-027, NS-028, NS-031, NS-033 · **Bloqueia:** NS-039, NS-064

- [ ] Todas as fichas e ataques executados 3 vezes, com a média registrada
- [ ] Consistência (meta < 5%), robustez (meta < 10%) e formato (meta 100%) calculados
- [ ] Relatório curto da rodada em `evals/resultados/`, com métricas, principais erros e custo em tokens
- [ ] Metas recalibradas, se necessário, com justificativa

### NS-035 — Implementar a autenticação no backend
`area:backend` `tipo:feature` · **Milestone:** Sprint 3 — Protótipo (C2) · **Responsável:** Davi · **Prioridade:** P1 · **Tamanho:** M · **RF:** RF01 · **Depende de:** – · **Bloqueia:** NS-036, NS-053

- [ ] Cadastro e login com dados mínimos: nome, e-mail e senha
- [ ] Senha armazenada com hash forte (por exemplo, Argon2 ou bcrypt)
- [ ] Sessões e casos associados ao usuário autenticado
- [ ] Rotas da simulação protegidas
- [ ] Testes de cadastro, login e acesso negado

### NS-036 — Criar as telas de cadastro e login
`area:frontend` `tipo:feature` · **Milestone:** Sprint 3 — Protótipo (C2) · **Responsável:** Pedro · **Prioridade:** P2 · **Tamanho:** M · **RF:** RF01 · **Depende de:** NS-035 · **Bloqueia:** –

- [ ] Formulários com validação e mensagens de erro claras
- [ ] Aviso de privacidade explicando quais dados são coletados e para quê (LGPD)
- [ ] Sessão mantida entre páginas, com botão de sair
- [ ] Acessível por teclado e por leitores de tela

### NS-037 — Criar a navegação entre as etapas da sessão
`area:frontend` `tipo:feature` · **Milestone:** Sprint 3 — Protótipo (C2) · **Responsável:** Pedro · **Prioridade:** P2 · **Tamanho:** M · **Depende de:** NS-021, NS-022 · **Bloqueia:** –

- [ ] Indicador da etapa atual (1 a 5) em todas as telas da sessão
- [ ] Estados padronizados de carregamento, erro e vazio
- [ ] Sessão em andamento retomada na etapa certa

### NS-038 — Publicar um preview no Render
`area:infra` `tipo:tarefa` · **Milestone:** Sprint 3 — Protótipo (C2) · **Responsável:** Mauro · **Prioridade:** P1 · **Tamanho:** M · **Depende de:** NS-011 · **Bloqueia:** NS-039, NS-058

Deploy antecipado para descobrir problemas de infraestrutura antes da Sprint 6.

- [ ] Backend e frontend publicados no Render (plano gratuito), usando a base de desenvolvimento do Neon
- [ ] Variáveis de ambiente configuradas no painel, sem segredos no repositório
- [ ] CORS liberado só para o domínio do frontend
- [ ] Tempo da primeira resposta depois da hibernação medido e anotado

### NS-039 — Gravar o vídeo do protótipo (C2)
`area:docs` `tipo:entrega` · **Milestone:** Sprint 3 — Protótipo (C2) · **Responsável:** Pedro (todos gravam) · **Prioridade:** P0 · **Tamanho:** M · **Depende de:** NS-034, NS-038 · **Bloqueia:** NS-040

- [ ] Roteiro cobrindo a rubrica da C2: IA funcionando, viabilidade técnica, testes e eval iniciais
- [ ] Demonstração do fluxo caso → anamnese e do motor calculando
- [ ] Resultados da primeira rodada de eval apresentados
- [ ] Vídeo publicado no YouTube (público ou não listado) até 28/10

### NS-040 — Entregar a C2 e fazer a autoavaliação e a avaliação 360°
`area:gestao` `tipo:entrega` · **Milestone:** Sprint 3 — Protótipo (C2) · **Responsável:** Mauro · **Prioridade:** P0 · **Tamanho:** P · **Depende de:** NS-039 · **Bloqueia:** –

- [ ] Links do vídeo e do repositório enviados no "Envio de Trabalho" da C2
- [ ] Repositório atualizado na data da entrega
- [ ] Autoavaliação e avaliação 360° preenchidas por cada integrante

---

## Sprint 4 — Plano e cenários (02/11 a 15/11)

### NS-041 — Criar os endpoints do plano alimentar
`area:backend` `tipo:feature` · **Milestone:** Sprint 4 — Plano e cenários · **Responsável:** Mauro · **Prioridade:** P1 · **Tamanho:** M · **RF:** RF05 · **Depende de:** NS-023 · **Bloqueia:** NS-042

- [ ] Salvar e editar o plano por refeição, com alimentos da TACO e porções em gramas
- [ ] Resposta com a composição calculada pelo motor (total e por refeição) e o GET do paciente
- [ ] Validação: só alimentos existentes na TACO e porções positivas
- [ ] Testes de integração

### NS-042 — Criar a tela de montagem do plano alimentar
`area:frontend` `tipo:feature` · **Milestone:** Sprint 4 — Plano e cenários · **Responsável:** Pedro · **Prioridade:** P2 · **Tamanho:** G · **RF:** RF05 · **Depende de:** NS-041, NS-044 · **Bloqueia:** –

- [ ] Refeições montadas com busca na TACO (autocompletar) e porção em gramas
- [ ] Totais de energia e nutrientes atualizados a cada mudança e comparados ao GET
- [ ] Alertas de restrição (NS-044) exibidos junto ao item que os causa
- [ ] Usável em 360 px e por teclado

### NS-043 — Montar a tabela de preços aproximados dos alimentos
`area:motor` `area:nutricao` `tipo:tarefa` · **Milestone:** Sprint 4 — Plano e cenários · **Responsável:** Mauro · **Prioridade:** P1 · **Tamanho:** M · **RF:** RF06 · **Depende de:** – · **Bloqueia:** NS-044

A TACO não tem preços, mas a restrição de orçamento do caso depende deles.

- [ ] Preço aproximado por 100 g, ou por unidade, dos alimentos mais usados nos planos
- [ ] Fonte e data de referência citadas (por exemplo, a cesta básica do DIEESE para Vitória, completada por levantamento próprio)
- [ ] Alimento sem preço tratado de forma explícita: o motor avisa que o custo está incompleto
- [ ] Tabela versionada em `backend/data/`

### NS-044 — Motor: verificar as restrições do caso
`area:motor` `tipo:feature` · **Milestone:** Sprint 4 — Plano e cenários · **Responsável:** Davi · **Prioridade:** P1 · **Tamanho:** M · **RF:** RF06 · **Depende de:** NS-043 · **Bloqueia:** NS-042, NS-055

- [ ] Limite de sódio, alimentos evitados e orçamento conferidos contra a ficha do caso
- [ ] Limites (por exemplo, de sódio) definidos com o professor de Nutrição e documentados com a fonte
- [ ] Cada violação aponta o alimento ou a refeição que a causou
- [ ] Testes por tipo de restrição

### NS-045 — Motor: projetar o peso e calcular o cenário ideal
`area:motor` `tipo:feature` · **Milestone:** Sprint 4 — Plano e cenários · **Responsável:** Mauro · **Prioridade:** P1 · **Tamanho:** G · **RF:** RF07, RF08 · **Depende de:** NS-024 · **Bloqueia:** NS-048, NS-055

- [ ] Projeção de peso para poucas semanas com a versão simplificada do modelo de Hall et al. (2011), sem a regra fixa de 7.700 kcal/kg
- [ ] Cenário de adesão ideal: o plano seguido integralmente
- [ ] Série semanal de peso e de adequação para os gráficos
- [ ] Limitação do modelo documentada, com o texto do aviso para a interface
- [ ] Testes com valores de referência

### NS-046 — Gerar o cenário de adesão realista com function calling
`area:llm` `area:backend` `tipo:feature` · **Milestone:** Sprint 4 — Plano e cenários · **Responsável:** Davi · **Prioridade:** P0 · **Tamanho:** G · **RF:** RF07 · **Depende de:** NS-013, NS-018 · **Bloqueia:** NS-047, NS-048, NS-050

- [ ] Prompt versionado que analisa o plano e o perfil e devolve, em JSON validado, a adesão estimada por refeição e as substituições prováveis
- [ ] Substituições escolhidas por uma ferramenta de busca na TACO, sem alimentos inventados
- [ ] Consumo realista convertido pelo motor em composição, peso e adequação; a IA não calcula números
- [ ] Teste de integração com LLM mockado

### NS-047 — Criar as regras de coerência entre perfil e cenário
`area:eval` `tipo:teste` · **Milestone:** Sprint 4 — Plano e cenários · **Responsável:** Arthur · **Prioridade:** P1 · **Tamanho:** M · **Depende de:** NS-046 · **Bloqueia:** NS-064

- [ ] Regras automáticas documentadas. Exemplos:
  - substituto que o paciente evita;
  - substituição que estoura o orçamento;
  - adesão incompatível com a rotina descrita
- [ ] Taxa de violações medida em um lote de cenários (meta < 5%)
- [ ] Regras integradas ao harness de eval

### NS-048 — Criar a tela de cenários
`area:frontend` `tipo:feature` · **Milestone:** Sprint 4 — Plano e cenários · **Responsável:** Pedro · **Prioridade:** P2 · **Tamanho:** G · **RF:** RF08 · **Depende de:** NS-045, NS-046 · **Bloqueia:** –

- [ ] Gráficos de peso e de adequação nos cenários ideal e realista
- [ ] Substituições do cenário realista listadas por refeição
- [ ] Aviso de limitação da projeção sempre visível
- [ ] Gráficos legíveis em 360 px e com alternativa em texto para leitores de tela

### NS-049 — Escrever a rubrica e os roteiros de anamnese
`area:nutricao` `area:docs` `tipo:tarefa` · **Milestone:** Sprint 4 — Plano e cenários · **Responsável:** Arthur · **Prioridade:** P0 · **Tamanho:** M · **Depende de:** NS-016 · **Bloqueia:** NS-051

Sai antes da Sprint 5 para dar tempo ao professor de revisar.

- [ ] Rubrica em `content/rubricas/` com critérios, pesos e exemplos por nível
- [ ] Roteiros de anamnese em `content/roteiros/` para cada perfil do MVP
- [ ] Front matter no formato do `content/README.md`
- [ ] Material enviado ao professor de Nutrição para revisão

---

## Sprint 5 — Retorno e rubrica (16/11 a 22/11)

### NS-050 — Implementar a consulta de retorno
`area:llm` `area:backend` `tipo:feature` · **Milestone:** Sprint 5 — Retorno e rubrica · **Responsável:** Mauro · **Prioridade:** P0 · **Tamanho:** M · **RF:** RF09 · **Depende de:** NS-046 · **Bloqueia:** NS-052

- [ ] Prompt versionado em que o paciente relata dificuldades coerentes com o cenário realista
- [ ] Mesmo streaming, histórico e proteções do paciente da anamnese
- [ ] Teste de integração com LLM mockado

### NS-051 — Implementar a avaliação por rubrica
`area:llm` `area:backend` `tipo:feature` · **Milestone:** Sprint 5 — Retorno e rubrica · **Responsável:** Davi · **Prioridade:** P0 · **Tamanho:** G · **RF:** RF10 · **Depende de:** NS-049 · **Bloqueia:** NS-052, NS-053, NS-056

- [ ] Prompt separado, o único com acesso ao gabarito da ficha
- [ ] Contexto recuperado de `content/` por filtro de metadados do perfil do caso
- [ ] Saída em JSON validado com nota por critério, pontos fortes, lacunas da anamnese e informações não descobertas
- [ ] Lista de informações ocultas descobertas e não descobertas, com o percentual calculado no backend (indicador do Quadro 4)
- [ ] Teste de integração com LLM mockado

### NS-052 — Criar as telas de retorno e de feedback
`area:frontend` `tipo:feature` · **Milestone:** Sprint 5 — Retorno e rubrica · **Responsável:** Pedro · **Prioridade:** P0 · **Tamanho:** M · **RF:** RF09, RF10 · **Depende de:** NS-050, NS-051 · **Bloqueia:** NS-058, NS-060

- [ ] Tela de retorno reaproveitando o chat da anamnese
- [ ] Tela de feedback com nota por critério, pontos fortes, lacunas e informações não descobertas
- [ ] Acesso à conversa completa da sessão a partir do feedback
- [ ] Acessível e usável em 360 px

### NS-053 — Criar o endpoint de histórico e evolução
`area:backend` `tipo:feature` · **Milestone:** Sprint 5 — Retorno e rubrica · **Responsável:** Mauro · **Prioridade:** P1 · **Tamanho:** M · **RF:** RF11 · **Depende de:** NS-035, NS-051 · **Bloqueia:** NS-054, NS-069

- [ ] Lista de sessões do estudante com data, perfil, dificuldade e nota da rubrica
- [ ] Evolução da nota e do percentual de informações descobertas ao longo das sessões
- [ ] Cada estudante vê só o próprio histórico
- [ ] Testes de integração

### NS-054 — Criar a tela de histórico e evolução
`area:frontend` `tipo:feature` · **Milestone:** Sprint 5 — Retorno e rubrica · **Responsável:** Pedro · **Prioridade:** P2 · **Tamanho:** M · **RF:** RF11 · **Depende de:** NS-053 · **Bloqueia:** –

- [ ] Lista de sessões com acesso ao feedback de cada uma
- [ ] Gráfico simples da evolução, com alternativa em texto
- [ ] Estado vazio para quem ainda não concluiu nenhuma sessão

### NS-055 — Testar as regras de restrição, adequação e projeção
`area:motor` `tipo:teste` · **Milestone:** Sprint 5 — Retorno e rubrica · **Responsável:** Davi · **Prioridade:** P2 · **Tamanho:** M · **Depende de:** NS-044, NS-045 · **Bloqueia:** –

- [ ] Cada tipo de restrição com casos que violam e casos que não violam
- [ ] Projeção de peso comparada a valores de referência calculados à mão
- [ ] Casos-limite: plano vazio, déficit ou superávit extremos, alimento sem preço
- [ ] Rodando na CI

### NS-056 — Validar a rubrica e os cenários com o professor de Nutrição
`area:eval` `area:nutricao` `tipo:teste` · **Milestone:** Sprint 5 — Retorno e rubrica · **Responsável:** Arthur · **Prioridade:** P1 · **Tamanho:** M · **Depende de:** NS-051 · **Bloqueia:** NS-064

- [ ] 20 consultas corrigidas pela IA e pelo professor, com kappa de Cohen calculado (meta ≥ 0,6) e interpretado segundo Landis e Koch (1977)
- [ ] 20 cenários de adesão avaliados pelo professor quanto ao realismo (meta: média ≥ 4 de 5)
- [ ] Resultados e ajustes salvos em `evals/resultados/`
- [ ] Pode terminar na Sprint 6 sem bloquear as sessões com estudantes

### NS-057 — Documentar a governança de IA
`area:docs` `tipo:tarefa` · **Milestone:** Sprint 5 — Retorno e rubrica · **Responsável:** Arthur · **Prioridade:** P1 · **Tamanho:** M · **Depende de:** – · **Bloqueia:** NS-059, NS-062

- [ ] `docs/governanca.md` cobrindo os quatro eixos obrigatórios do edital
- [ ] **Privacidade e LGPD:** dados coletados, base legal, minimização e anonimização
- [ ] **Segurança:** riscos de prompt injection e de uso indevido, com as mitigações adotadas
- [ ] **Ética e viés:** limitações do modelo, diversidade dos perfis e cuidados na comunicação dos resultados
- [ ] **Custo e sustentabilidade:** tokens por consulta medidos, número de chamadas e limites do plano gratuito

---

## Sprint 6 — Deploy e sessões (23/11 a 29/11)

### NS-058 — Publicar o MVP em produção
`area:infra` `tipo:entrega` · **Milestone:** Sprint 6 — Deploy e sessões · **Responsável:** Davi · **Prioridade:** P0 · **Tamanho:** M · **Depende de:** NS-038, NS-052 · **Bloqueia:** NS-063, NS-067

- [ ] Backend e frontend em produção no Render, usando a base de produção do Neon com as migrações aplicadas
- [ ] URL pública estável, anotada no README
- [ ] Tempo até o início da resposta do paciente medido (meta: até 3 s), com o atraso depois da hibernação documentado
- [ ] Passo a passo de deploy e de reversão no README

### NS-059 — Reforçar segurança e custo
`area:backend` `area:llm` `tipo:tarefa` · **Milestone:** Sprint 6 — Deploy e sessões · **Responsável:** Mauro · **Prioridade:** P2 · **Tamanho:** M · **Depende de:** NS-057 · **Bloqueia:** –

- [ ] Limite de requisições por usuário nas rotas que chamam o LLM
- [ ] Revisão de segredos: nenhuma chave no repositório, no frontend ou nos logs
- [ ] Cache de respostas onde a entrada se repete
- [ ] Tokens por sessão consolidados e visíveis para a equipe
- [ ] Modelo menor avaliado nas tarefas simples

### NS-060 — Escrever os testes de ponta a ponta com Playwright
`area:frontend` `tipo:teste` · **Milestone:** Sprint 6 — Deploy e sessões · **Responsável:** Davi · **Prioridade:** P2 · **Tamanho:** M · **Depende de:** NS-052 · **Bloqueia:** –

- [ ] Fluxo principal percorrido: login → caso → anamnese → plano → cenários → retorno → feedback
- [ ] Backend rodando com um LLM falso, ativado por variável de ambiente, para resultados reproduzíveis
- [ ] Executado em viewport de celular (360 px) e de desktop
- [ ] Rodando na CI

### NS-061 — Auditar a acessibilidade e a responsividade
`area:frontend` `tipo:teste` · **Milestone:** Sprint 6 — Deploy e sessões · **Responsável:** Pedro · **Prioridade:** P2 · **Tamanho:** M · **Depende de:** – · **Bloqueia:** –

- [ ] Auditoria automática (por exemplo, Lighthouse ou axe) em todas as telas, sem erros críticos
- [ ] Navegação completa por teclado, com foco visível
- [ ] Teste manual com leitor de tela no fluxo principal
- [ ] Contraste no nível WCAG AA e nenhuma rolagem horizontal a partir de 360 px

### NS-062 — Preparar o termo de consentimento e os questionários
`area:gestao` `area:docs` `tipo:tarefa` · **Milestone:** Sprint 6 — Deploy e sessões · **Responsável:** Arthur · **Prioridade:** P1 · **Tamanho:** M · **Depende de:** NS-057 · **Bloqueia:** NS-063

- [ ] Termo de consentimento com finalidade, dados coletados, anonimização e direito de desistir. A base legal é o consentimento (LGPD)
- [ ] Questionário SUS (BROOKE, 1996) para depois do uso
- [ ] Escala Likert de autoconfiança antes e depois do uso, com pergunta aberta
- [ ] Avaliação do realismo do paciente e dos cenários (1 a 5)
- [ ] Formulários prontos, sem coletar dados além do necessário

### NS-063 — Conduzir as sessões de uso com estudantes
`area:nutricao` `area:gestao` `tipo:entrega` · **Milestone:** Sprint 6 — Deploy e sessões · **Responsável:** Arthur (todos conduzem sessões) · **Prioridade:** P0 · **Tamanho:** G · **Depende de:** NS-058, NS-062 · **Bloqueia:** NS-065

- [ ] Consentimento de cada participante registrado antes do uso
- [ ] Cada participante com pelo menos 3 consultas simuladas
- [ ] Questionários aplicados antes e depois
- [ ] Dados anonimizados antes de entrarem no repositório
- [ ] Número de participantes e de sessões concluídas registrado (indicador de alcance)

---

## Sprint 7 — MVP (C3) (30/11 a 04/12)

### NS-064 — Executar a rodada final de eval
`area:eval` `tipo:teste` · **Milestone:** Sprint 7 — MVP (C3) · **Responsável:** Arthur (apoio: Davi) · **Prioridade:** P0 · **Tamanho:** M · **Depende de:** NS-034, NS-047, NS-056 · **Bloqueia:** NS-067, NS-068

- [ ] Todas as métricas do Quadro 3 medidas na versão final dos prompts
- [ ] Comparação com a primeira rodada: o que melhorou, o que piorou e por quê
- [ ] Custo total em tokens das rodadas registrado
- [ ] Resultados em `evals/resultados/`, com resumo na documentação

### NS-065 — Analisar o impacto
`area:docs` `area:nutricao` `tipo:entrega` · **Milestone:** Sprint 7 — MVP (C3) · **Responsável:** Arthur · **Prioridade:** P0 · **Tamanho:** M · **Depende de:** NS-063 · **Bloqueia:** NS-067, NS-068

- [ ] Nota da rubrica na 1ª e na 3ª sessão de cada participante
- [ ] Percentual de informações ocultas descobertas, da 1ª à 3ª sessão
- [ ] Média do SUS (meta ≥ 68), autoconfiança antes e depois e percepção de realismo (meta ≥ 4)
- [ ] Alcance: número de estudantes e de sessões concluídas
- [ ] Análise das respostas abertas e das limitações do estudo

### NS-066 — Finalizar a documentação
`area:docs` `tipo:entrega` · **Milestone:** Sprint 7 — MVP (C3) · **Responsável:** Mauro · **Prioridade:** P1 · **Tamanho:** M · **Depende de:** – · **Bloqueia:** NS-068

- [ ] README com como rodar, a URL pública e o estado final do projeto
- [ ] Arquitetura, decisões, governança e eval revisados e atualizados
- [ ] Limitações do sistema documentadas
- [ ] `docs/prompts/` com todos os usos de IA registrados

### NS-067 — Gravar o vídeo do MVP (C3)
`area:docs` `tipo:entrega` · **Milestone:** Sprint 7 — MVP (C3) · **Responsável:** Pedro (todos gravam) · **Prioridade:** P0 · **Tamanho:** M · **Depende de:** NS-058, NS-064, NS-065 · **Bloqueia:** NS-068

- [ ] Roteiro cobrindo a rubrica da C3:
  - funcionalidade, usabilidade e inovação;
  - IA e eval;
  - testes;
  - deploy, documentação e código;
  - impacto e IA responsável
- [ ] Demonstração do fluxo completo na URL pública, no celular e no computador
- [ ] Resultados do eval e da análise de impacto apresentados
- [ ] Vídeo publicado no YouTube até 03/12

### NS-068 — Entregar a C3 e fazer a autoavaliação e a avaliação 360°
`area:gestao` `tipo:entrega` · **Milestone:** Sprint 7 — MVP (C3) · **Responsável:** Mauro · **Prioridade:** P0 · **Tamanho:** P · **Depende de:** NS-064, NS-065, NS-066, NS-067 · **Bloqueia:** –

- [ ] Links do vídeo, do repositório e da URL pública enviados no "Envio de Trabalho" da C3 até 03/12
- [ ] Repositório com código, testes, eval e documentação atualizados
- [ ] Autoavaliação e avaliação 360° feitas por cada integrante

---

## Backlog (desejável, sem milestone)

### NS-069 — Criar o painel do professor
`area:frontend` `area:backend` `tipo:feature` · **Milestone:** – · **Responsável:** Pedro (apoio: Davi) · **Prioridade:** P3 · **Tamanho:** G · **RF:** RF12 · **Depende de:** NS-053 · **Bloqueia:** –

Requisito desejável. Só entra se as sprints anteriores fecharem com folga.

- [ ] Perfil de acesso de professor
- [ ] Revisão dos perfis de paciente
- [ ] Resultados agregados e anonimizados das sessões (notas médias, informações mais esquecidas)

---

## Cobertura do relatório

| Item do relatório | Cards |
|---|---|
| RF01: cadastro e autenticação | NS-035, NS-036 |
| RF02: seleção de perfil e dificuldade | NS-019, NS-021 |
| RF03: geração de caso com ficha oculta | NS-014, NS-019 |
| RF04: entrevista em tempo real | NS-020, NS-022 |
| RF05: plano com busca na TACO e cálculo | NS-013, NS-023, NS-024, NS-041, NS-042 |
| RF06: verificação de restrições | NS-043, NS-044 |
| RF07: cenários de adesão | NS-045, NS-046 |
| RF08: projeção de peso e adequação com gráficos | NS-025, NS-045, NS-048 |
| RF09: consulta de retorno | NS-050, NS-052 |
| RF10: feedback por rubrica | NS-051, NS-052 |
| RF11: histórico e evolução | NS-053, NS-054 |
| RF12: painel do professor (desejável) | NS-069 |
| Requisitos não funcionais (seção 3.3) | NS-009, NS-020, NS-058, NS-061, NS-066 |
| Tarefas de IA (seção 4.3) | NS-019, NS-020, NS-046, NS-050, NS-051 |
| Testes (seção 4.5) | NS-011, NS-029, NS-030, NS-055, NS-060 |
| Métricas de eval (Quadro 3) | NS-033, NS-034, NS-047, NS-056, NS-064 |
| IA responsável (seção 4.7) | NS-057, NS-059, NS-062 |
| Indicadores de impacto (Quadro 4) | NS-063, NS-065 |
