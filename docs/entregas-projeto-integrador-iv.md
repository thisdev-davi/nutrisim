# Projeto Integrador IV (2026/2) — o que precisa ser entregue

Resumo do edital para acompanhamento do grupo.
Disciplina: Aplicações de Inteligência Artificial · Prof. M.Sc. Howard Cruz Roatti (howard.cruz@faesa.br)
Áreas temáticas: Direitos Humanos e Justiça · Saúde · Tecnologia e Inovação · Trabalho e Empreendedorismo
ODS: 3, 4, 8, 9 e 12

> O edital é vivo e pode ser atualizado durante o semestre. Confira a versão mais recente antes de cada entrega.

## Prazos

| Entrega | O que enviar | Prazo |
|---|---|---|
| **C1 — Relatório** | Escopo, justificativa, metodologia, plano de trabalho e comunidade impactada com indicadores previstos. GitHub inicial. | **18/09/2026** |
| **C2 — Protótipo** | Vídeo no YouTube com o protótipo e a viabilidade técnica: IA em funcionamento e primeiros testes/eval. | **30/10/2026** |
| **C3 — MVP** | Vídeo no YouTube do MVP, documentação, código-fonte, testes e eval, URL pública do deploy e análise de impacto. | **04/12/2026** |

Cada entrega vai no "Envio de Trabalho" correspondente, com o link do vídeo ou do repositório, e o GitHub precisa estar atualizado.

## Avaliação

Cada checkpoint vale 10,0 pontos:

- **6,0 — nota do grupo** (qualidade técnica)
- **4,0 — nota individual** (autoavaliação + avaliação 360° entre pares, modelo na planilha do Quadro de Avaliações)

A não entrega dos artefatos afeta todo o grupo. A avaliação é contínua.

Rubrica da nota do grupo:

- **C1:** problema e metodologia (40%) · comunidade e indicadores (30%) · organização inicial e GitHub (30%)
- **C2:** funcionamento do componente de IA (40%) · viabilidade técnica (30%) · testes/eval iniciais e vídeo (30%)
- **C3:** funcionalidade, usabilidade e inovação (35%) · qualidade da IA e sua eval (25%) · testes automatizados (15%) · deploy, documentação e código (15%) · impacto e IA responsável (10%)

## Requisitos técnicos

- [ ] Aplicação completa, web ou mobile, com backend e frontend
- [ ] Componente de IA obrigatório, com LLM via API (Groq é o recomendado; outros provedores gratuitos e modelos open-weight locais são aceitos)
- [ ] Engenharia de contexto: prompts bem definidos e, quando fizer sentido, RAG, tool/function calling, agentes e multimodalidade
- [ ] Testes automatizados (unitários e de integração) das partes críticas
- [ ] Harness de eval do componente de IA medindo relevância, taxa de erro/alucinação e robustez, com as métricas documentadas
- [ ] Deploy do MVP em nuvem free tier (ex.: Render, Railway) com URL pública
- [ ] Repositório no GitHub atualizado a cada entrega, com código e documentação
- [ ] Professor adicionado como colaborador do repositório

## IA responsável e governança (obrigatório)

- [ ] **Privacidade e LGPD:** dados usados, base legal, minimização e anonimização
- [ ] **Segurança:** riscos de prompt injection e uso indevido, com as mitigações adotadas
- [ ] **Ética e viés:** limitações do modelo e cuidados na comunicação dos resultados
- [ ] **Custo e sustentabilidade:** noção de uso (tokens e chamadas) e atenção aos limites do plano gratuito

## Natureza extensionista

- [ ] Comunidade impactada identificada e caracterizada (não precisa participar, mas deve ser analisada)
- [ ] Indicadores de impacto (quantitativos e/ou qualitativos) e como serão medidos
- [ ] Análise de impacto na entrega final (C3)

Fontes sugeridas pelo edital: IBGE, DATASUS, Kaggle, portais governamentais, escolas, universidades, hospitais, ONGs, pequenos negócios e startups, problemas urbanos e ambientais.

## Grupo

- [ ] Até 5 integrantes
- [ ] Composição informada ao professor por e-mail
- [ ] Inscrição no grupo correspondente no AVA

Entrega coletiva pelo GitHub, com avaliação individual.

## Integridade acadêmica

- [ ] Projeto original, sem cópias
- [ ] Uso de IA no desenvolvimento compreendido e documentado pelo grupo
- [ ] **Todo processo de engenharia de software feito com auxílio de IA registrado no repositório, com o prompt utilizado para a tarefa**

## Ferramentas de apoio citadas no edital

- Groq (GroqCloud): LLMs abertos gratuitos via API, compatível com a API da OpenAI (passo a passo na sessão "Acesso gratuito a LLMs com o Groq")
- GitHub: versionamento e entrega, com o professor como colaborador
- YouTube: vídeos da C2 e da C3
- Nuvem free tier (Render/Railway) para o deploy
- Outras opções gratuitas: modelos open-weight locais (ex.: via Ollama) e outros provedores com free tier

## Situação do grupo (NutriSim)

- [x] Tema definido: simulador de pacientes com IA para estudantes de Nutrição
- [x] Relatório da C1 escrito em ABNT
- [ ] Preencher o link do repositório e a meta de alcance no relatório
- [ ] Criar o repositório com a estrutura de pastas e adicionar o professor
- [ ] Salvar em `docs/prompts/` os prompts usados na elaboração do relatório
- [ ] Informar a composição do grupo ao professor e se inscrever no AVA
- [ ] Enviar o relatório no Envio de Trabalho da C1
