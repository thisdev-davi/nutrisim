# Registro de decisões de arquitetura (ADRs)

Cada decisão importante fica registrada aqui, com contexto e consequências, para que a equipe e os avaliadores entendam o porquê das escolhas.

**Como registrar uma nova decisão:** copie o modelo no fim do arquivo, use o próximo número e abra um PR. Com o PR aprovado, a decisão fica com status *aceita*. Uma decisão substituída não é apagada: o status passa para *substituída por ADR-XXX*.

---

## ADR-001 — Separar o comportamento (IA) da fisiologia (motor determinístico)

**Status:** aceita · **Data:** 18/09/2026

**Contexto.** LLMs podem produzir informações falsas com aparência plausível, o que é grave em uma ferramenta de formação em saúde. Um LLM pedido para "simular os resultados" de uma dieta devolveria números inventados. O edital também exige medir a taxa de erro e alucinação do componente de IA.

**Decisão.** O LLM atua só no comportamento do paciente: gerar o caso, conversar, estimar a adesão realista, relatar o retorno e corrigir pela rubrica. Composição nutricional, necessidade energética, adequação e projeção de peso ficam em um motor determinístico em Python, baseado na TACO (NEPA, 2011), em Mifflin-St Jeor (1990), nas DRIs (IOM, 2006) e em Hall et al. (2011).

**Consequências.**
- (+) O cálculo é testável com contas feitas à mão, e os números mostrados ao estudante têm fonte publicada.
- (+) O eval se concentra no que a IA realmente faz: consistência, robustez e realismo.
- (−) São dois componentes a integrar, e a IA precisa devolver saídas estruturadas que o motor consiga consumir.
- (−) Desfechos clínicos, como glicemia ou pressão arterial, ficam fora do escopo. As doenças entram só como restrições verificáveis.

---

## ADR-002 — Stack: Next.js + Tailwind, FastAPI, PostgreSQL (Neon) e Render

**Status:** aceita · **Data:** 18/09/2026

**Contexto.** O sistema precisa rodar no celular e no computador, fazer cálculos nutricionais, executar evals em Python e caber em planos gratuitos de infraestrutura.

**Decisão.**
- **Frontend:** Next.js (React) com Tailwind CSS, com uma única base responsiva, pensada primeiro para o celular.
- **Backend:** FastAPI (Python), que é assíncrono, valida dados com Pydantic e compartilha o ecossistema do motor e do eval.
- **Banco:** PostgreSQL no Neon. O plano gratuito não expira, ao contrário do Postgres gratuito do Render.
- **Deploy:** Render, com backend e frontend em plano gratuito e URL pública.
- **Testes e CI:** pytest, Playwright e GitHub Actions em todo pull request.

**Consequências.**
- (+) Os mesmos modelos Pydantic servem ao contrato da API, à validação do LLM e ao eval.
- (−) São dois serviços para publicar e configurar, incluindo o CORS entre eles.
- (−) O plano gratuito do Render hiberna quando fica sem uso, e o atraso da primeira requisição precisa ser medido e documentado (NS-058).

---

## ADR-003 — Gemini Flash para o paciente, Groq para o juiz e modelo definido por variável de ambiente

**Status:** aceita · **Data:** 18/09/2026

**Contexto.** O edital recomenda o Groq, mas aceita outros provedores gratuitos. As tarefas do produto precisam de saída estruturada por JSON schema, de chamada de ferramentas (busca na TACO) e de contexto longo, porque o histórico da conversa é reenviado a cada turno. O eval precisa de um juiz que não favoreça as respostas do próprio modelo (ZHENG et al., 2023).

**Decisão.**
- As cinco tarefas do produto usam um modelo da linha **Gemini Flash**, via Google AI Studio.
- O **juiz do eval** usa um modelo aberto hospedado no **Groq**, de família diferente da usada pelo paciente.
- O nome de cada modelo vem de **variável de ambiente**, nunca fixado no código.

**Consequências.**
- (+) As saídas estruturadas e o function calling nativos reduzem o código de validação.
- (+) Um modelo descontinuado pode ser trocado sem mudar código, e a bateria de eval valida a troca.
- (−) São duas chaves e dois conjuntos de limites de uso. É preciso ter cache de respostas, registro de tokens por chamada e evals executados em lotes.

---

## ADR-004 — Recuperação por filtro de metadados, sem banco vetorial

**Status:** aceita · **Data:** 18/09/2026

**Contexto.** A avaliação por rubrica precisa de contexto: os critérios do curso de Nutrição e os roteiros de anamnese de cada perfil. Esse material é pequeno, fica em Markdown e é revisado por professores sem conhecimento técnico.

**Decisão.** Os arquivos de `content/` têm um cabeçalho de metadados com os perfis a que se aplicam. A avaliação carrega as seções do perfil do caso por filtro de metadados, sem embeddings nem banco vetorial.

**Consequências.**
- (+) A recuperação é simples, determinística e não exige infraestrutura extra.
- (+) Os professores editam texto comum, e o histórico das revisões fica no Git.
- (−) Se o material crescer além do contexto disponível, será preciso adotar busca por similaridade, registrada em uma nova ADR.

---

## Modelo

```markdown
## ADR-XXX — Título curto da decisão

**Status:** proposta | aceita | substituída por ADR-XXX · **Data:** DD/MM/AAAA

**Contexto.** Qual problema ou restrição motivou a decisão.

**Decisão.** O que foi decidido.

**Consequências.**
- (+) ganhos
- (−) custos e riscos
```
