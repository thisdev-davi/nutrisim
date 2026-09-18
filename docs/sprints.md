# Sprints

As sprints seguem o cronograma do relatório (Quadro 5) e os checkpoints do edital. Cada sprint é um **milestone** no GitHub, com vencimento no último dia. Os cards de cada uma estão em [`kanban.md`](kanban.md).

## Calendário

| Sprint | Período | Dias úteis | Meta | Marco |
|---|---|---|---|---|
| Sprint 0 — C1 | até 18/09 | – | Entregar a C1 com o repositório organizado | **C1 (18/09)** |
| Sprint 1 — Fundação | 21/09 a 04/10 | 10 | Base pronta para trabalho em paralelo | – |
| Sprint 2 — Paciente e motor | 05/10 a 18/10 | 9 (12/10 é feriado) | Conversa com o paciente gerado e motor calculando | – |
| Sprint 3 — Protótipo (C2) | 19/10 a 30/10 | 10 | IA funcionando, primeiros testes e eval | **C2 (30/10)** |
| Sprint 4 — Plano e cenários | 02/11 a 15/11 | 9 (02/11 é feriado) | Etapas 3 e 4 funcionando | – |
| Sprint 5 — Retorno e rubrica | 16/11 a 22/11 | 4 (20/11 é feriado) | Fluxo completo, da etapa 1 à 5 | – |
| Sprint 6 — Deploy e sessões | 23/11 a 29/11 | 5 | MVP público e indicadores coletados | congelamento de funcionalidades |
| Sprint 7 — MVP (C3) | 30/11 a 04/12 | 5 | Entregar a C3 | **C3 (04/12)** |

Há um desvio intencional em relação ao relatório: um **deploy de preview na Sprint 3** (NS-038). Assim, problemas de infraestrutura aparecem cedo, e não na Sprint 6. O Quadro 5 continua valendo, porque o deploy de produção segue na Sprint 6.

## Rituais

| Ritual | Quando | Duração | O que acontece |
|---|---|---|---|
| Planejamento | segunda-feira de início da sprint | 30 min | revisar a meta, mover os cards do *Backlog* para *A fazer*, confirmar responsáveis e dependências |
| Acompanhamento | 2 vezes por semana, assíncrono no grupo | – | cada um escreve "fiz / vou fazer / bloqueio"; card travado recebe a label `bloqueado` |
| Revisão e retrospectiva | último dia útil da sprint | 30 min | demonstrar o que ficou pronto, devolver ao *Backlog* o que não ficou e responder "manter / mudar / tentar" |

Nos checkpoints (Sprints 0, 3 e 7), cada integrante também faz a **autoavaliação e a avaliação 360°**, que valem 4,0 pontos da nota individual.

---

## Sprint 0 — C1 · até 18/09

**Meta:** entregar a C1 com o repositório organizado. Na nota do grupo, a C1 pesa assim: problema e metodologia 40%, comunidade e indicadores 30%, organização inicial e GitHub 30%.

**Pronto quando:**
- [ ] o repositório está publicado com esta estrutura, e o professor foi adicionado como colaborador;
- [ ] a `main` está protegida;
- [ ] o quadro está montado, com os cards importados;
- [ ] o relatório está com os destaques preenchidos e foi enviado no AVA;
- [ ] a autoavaliação e a avaliação 360° foram feitas.

**Cards:** NS-001 a NS-006.

**Atenção:** o prazo é hoje. Priorizem NS-001, NS-003 e NS-006. Se o tempo apertar, importem primeiro os cards das Sprints 0 e 1.

## Sprint 1 — Fundação · 21/09 a 04/10

**Meta:** base pronta para os quatro trabalharem em paralelo.

**Pronto quando:**
- [ ] a `main` está protegida, com CI verde em todo PR;
- [ ] backend e frontend rodam localmente seguindo os READMEs;
- [ ] a TACO está importada no Neon, e a busca de alimentos responde;
- [ ] o contrato da API (`docs/api.md`) e o schema da ficha oculta foram aprovados pela equipe;
- [ ] os perfis do MVP estão definidos, e a reunião com o curso de Nutrição aconteceu.

**Cards:** NS-007 a NS-017.

**Atenção:** o contrato da API e o schema da ficha destravam as sprints seguintes, então fechem os dois na primeira semana. Confirmem com o professor se as sessões com estudantes dispensam apreciação do CEP.

## Sprint 2 — Paciente e motor · 05/10 a 18/10

**Meta:** conversar com um paciente gerado a partir de uma ficha oculta, com o motor já calculando.

**Pronto quando:**
- [ ] o estudante escolhe perfil e dificuldade e conversa em streaming com o paciente;
- [ ] a ficha oculta é validada e nunca chega ao frontend;
- [ ] o motor calcula composição, GET e adequação de uma lista de alimentos;
- [ ] o harness executa ao menos uma ficha de ponta a ponta e salva o resultado;
- [ ] os tokens são registrados em cada chamada ao LLM.

**Cards:** NS-018 a NS-028.

**Atenção:** o feriado de 12/10 cai nesta sprint. Durante o desenvolvimento, usem respostas gravadas nos testes para não gastar o limite gratuito do Gemini.

## Sprint 3 — Protótipo (C2) · 19/10 a 30/10

**Meta:** entregar a C2. Na nota, a C2 pesa assim: funcionamento da IA 40%, viabilidade técnica 30%, testes/eval e vídeo 30%.

**Pronto quando:**
- [ ] os testes unitários do motor e os de integração rodam na CI;
- [ ] o juiz foi validado, com o acerto medido em 50 vereditos;
- [ ] a 1ª rodada de eval de consistência e robustez está publicada em `evals/resultados/`;
- [ ] o preview está publicado no Render;
- [ ] o vídeo está no YouTube, a entrega foi feita no AVA e a autoavaliação e a 360° estão preenchidas.

**Cards:** NS-029 a NS-040.

**Atenção:** gravem o vídeo até 28/10 para ter folga. Se o juiz ficar abaixo de 85% de acerto, ajustem o prompt dele antes da rodada de eval.

## Sprint 4 — Plano e cenários · 02/11 a 15/11

**Meta:** etapas 3 e 4 funcionando.

**Pronto quando:**
- [ ] o plano é montado com busca na TACO, e os totais aparecem em tempo real;
- [ ] as restrições do caso são conferidas (sódio, alimentos evitados, orçamento);
- [ ] os cenários ideal e realista aparecem com gráficos de peso e adequação e com o aviso de limitação;
- [ ] as regras de coerência medem o cenário realista;
- [ ] a rubrica e os roteiros foram enviados ao professor de Nutrição.

**Cards:** NS-041 a NS-049.

**Atenção:**
- O feriado de 02/11 cai nesta sprint.
- No modelo de Hall, comecem pela versão mais simples e documentem a limitação.
- A TACO não tem preços, então a tabela de preços (NS-043) precisa sair no começo da sprint.
- A rubrica é enviada nesta sprint para o professor ter tempo de revisar.

## Sprint 5 — Retorno e rubrica · 16/11 a 22/11

**Meta:** fluxo completo, da etapa 1 à 5.

**Pronto quando:**
- [ ] a consulta de retorno é coerente com o cenário realista;
- [ ] o feedback por rubrica mostra pontos fortes, lacunas e informações não descobertas;
- [ ] o histórico de sessões mostra a evolução do desempenho;
- [ ] a governança de IA está documentada em `docs/governanca.md`;
- [ ] a validação com o professor começou (20 consultas e 20 cenários).

**Cards:** NS-050 a NS-057.

**Atenção:** é uma sprint de 4 dias úteis. A validação do professor pode terminar na Sprint 6 sem bloquear as sessões com estudantes.

## Sprint 6 — Deploy e sessões · 23/11 a 29/11

**Meta:** MVP público e indicadores de impacto coletados.

**Pronto quando:**
- [ ] a URL pública está estável, com o tempo de "despertar" do serviço medido;
- [ ] os testes E2E (celular e desktop) rodam na CI;
- [ ] há limite de requisições por usuário, e a revisão de segredos foi feita;
- [ ] as sessões com estudantes aconteceram, com consentimento e dados anonimizados;
- [ ] as **funcionalidades estão congeladas**: daqui em diante, só correções.

**Cards:** NS-058 a NS-063.

**Atenção:** as sessões dependem da agenda do curso, que precisa estar combinada desde a Sprint 1. Cada sessão dura no máximo 30 minutos.

## Sprint 7 — MVP (C3) · 30/11 a 04/12

**Meta:** entregar a C3. Na nota, a C3 pesa assim: funcionalidade, usabilidade e inovação 35%; IA e eval 25%; testes 15%; deploy, documentação e código 15%; impacto e IA responsável 10%.

**Pronto quando:**
- [ ] a rodada final de eval foi feita e comparada com a primeira;
- [ ] a análise de impacto cobre os indicadores do Quadro 4;
- [ ] a documentação final está pronta, e o `docs/prompts` está em dia;
- [ ] o vídeo do MVP está no YouTube;
- [ ] a entrega foi feita no AVA **até 03/12**, com um dia de folga, e a autoavaliação e a 360° estão preenchidas.

**Cards:** NS-064 a NS-068.

---

## Registro das revisões

Preenchido na revisão de cada sprint.

| Sprint | Concluído | Ficou para a próxima | Retro: manter / mudar / tentar |
|---|---|---|---|
| 0 | – | – | – |
| 1 | – | – | – |
| 2 | – | – | – |
| 3 | – | – | – |
| 4 | – | – | – |
| 5 | – | – | – |
| 6 | – | – | – |
| 7 | – | – | – |
