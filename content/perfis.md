---
tipo: perfis
versao: 1
# pendente de validação do professor de Nutrição (NS-016)
revisado_por:
revisado_em:
---

# Perfis do MVP e níveis de dificuldade

Este documento define **quais pacientes o NutriSim simula** e **o que muda entre os níveis de dificuldade**. A geração de caso (NS-019) usa estas definições para montar a ficha oculta, o schema da ficha (NS-014) precisa comportar os campos listados aqui, e as fichas de eval (NS-027) cobrem cada perfil.

Card: NS-015. Responsável: Arthur Pomarolli.

## Regras que todos os perfis seguem

1. **Casos sintéticos.** Nenhum perfil se baseia em paciente real (relatório C1, seção 1.3).
2. **Doença é restrição, não desfecho.** A condição clínica entra como uma restrição que o motor confere no plano, por exemplo um limite de sódio. O sistema nunca simula pressão arterial, glicemia ou exames (relatório C1, seção 3.4a).
3. **Fora do MVP:** perfis pediátricos, de gestantes e de atletas (relatório C1, seção 3.4c).
4. **Os valores de restrição vêm de diretrizes publicadas**, citadas nas referências. A equipe pode ajustá-los depois de testar os casos.

## Perfis

São cinco perfis. Quatro têm como conduta esperada um plano alimentar. Em um deles a conduta esperada é o **encaminhamento**, e o nome desse perfil não denuncia isso: identificar os sinais faz parte do exercício.

| ID | Nome na tela | Faixa etária | Restrição verificável pelo motor | Conduta esperada |
|---|---|---|---|---|
| `adulto-hipertensao` | Adulto com hipertensão | 40 a 60 anos | sódio ≤ 2.000 mg/dia | plano alimentar |
| `adulto-diabetes-tipo2` | Adulto com diabetes tipo 2 | 40 a 65 anos | fibras ≥ 14 g/1.000 kcal | plano alimentar |
| `adulto-dislipidemia` | Adulto com colesterol alto | 30 a 60 anos | gordura saturada < 10% do VET | plano alimentar |
| `idoso-baixa-ingestao` | Pessoa idosa com perda de apetite | 65 a 80 anos | proteína entre 1,2 e 1,5 g/kg/dia | plano alimentar |
| `adulto-jovem-emagrecimento` | Adulto jovem que quer emagrecer | 18 a 30 anos | – | **encaminhamento** |

VET: valor energético total do plano.

### Adulto com hipertensão (`adulto-hipertensao`)

- **Quadro:** hipertensão diagnosticada, em geral com excesso de peso. Pode usar anti-hipertensivo, mas a ficha só registra o que o paciente sabe dizer ("tomo um remédio de pressão de manhã").
- **Restrição:** sódio ≤ 2.000 mg/dia, o equivalente a cerca de 5 g de sal (OMS; Diretrizes Brasileiras de Hipertensão Arterial, 2020).
- **O que o estudante precisa investigar:** sal de adição e temperos prontos, embutidos e ultraprocessados, refeições fora de casa, consumo de álcool.
- **Exemplos de informação omitida:** usa tempero pronto em cubo "só às vezes", que na verdade é diariamente; almoça em restaurante por quilo nos dias úteis.

### Adulto com diabetes tipo 2 (`adulto-diabetes-tipo2`)

- **Quadro:** diabetes tipo 2 diagnosticado, com ou sem excesso de peso.
- **Restrição:** fibras ≥ 14 g por 1.000 kcal (Sociedade Brasileira de Diabetes, 2023).
- **Alimentos evitados:** bebidas adoçadas e doces. A TACO não tem coluna de açúcares, então o limite de açúcares de adição da OMS (< 10% do VET) não vira número no motor: o motor confere os alimentos evitados (NS-044) e a rubrica avalia a orientação (NS-049).
- **O que o estudante precisa investigar:** horários e fracionamento das refeições, bebidas adoçadas e sucos, doces, quantidade de carboidratos por refeição.
- **Exemplos de informação omitida:** troca o almoço por um lanche quando o trabalho aperta; toma suco de caixinha achando que "é saudável".

### Adulto com colesterol alto (`adulto-dislipidemia`)

- **Quadro:** colesterol LDL elevado, relatado pelo paciente ("o médico disse que meu colesterol está alto"). O sistema não gera valores de exame.
- **Restrição:** gordura saturada < 10% do VET (OMS).
- **O que o estudante precisa investigar:** carnes gordas, frituras, laticínios integrais, manteiga, preparações típicas de fim de semana.
- **Exemplos de informação omitida:** churrasco ou feijoada todo fim de semana; frita os alimentos em banha.

### Pessoa idosa com perda de apetite (`idoso-baixa-ingestao`)

- **Quadro:** ingestão reduzida e perda de peso não intencional nos últimos meses. Mora sozinha ou com um familiar.
- **Restrição:** proteína entre 1,2 e 1,5 g/kg/dia. O PROT-AGE (Bauer et al., 2013) indica 1,0 a 1,2 g/kg para idosos saudáveis e 1,2 a 1,5 g/kg para idosos com doença aguda ou crônica; a perda de peso não intencional indica risco de desnutrição, por isso vale a faixa maior.
- **O que o estudante precisa investigar:** quem compra e quem prepara a comida, dificuldade de mastigação, refeições puladas, solidão no horário das refeições.
- **Exemplos de informação omitida:** usa prótese dentária que machuca, por isso evita carne; o jantar costuma ser só café com pão.

### Adulto jovem que quer emagrecer (`adulto-jovem-emagrecimento`)

- **Quadro:** chega pedindo uma dieta para emagrecer, mas tem peso adequado para a altura. Ao longo da anamnese, aparecem **sinais de alerta de transtorno alimentar**: restrição alimentar intensa, medo de ganhar peso, pular refeições como regra, exercício para "compensar" o que comeu, preocupação constante com o corpo.
- **Conduta esperada:** acolher, **não prescrever dieta restritiva** e encaminhar para avaliação com a equipe multiprofissional (psicologia e psiquiatria), mantendo o acompanhamento nutricional.
- **O que o estudante precisa investigar:** histórico de peso, frequência das refeições, comportamentos compensatórios, como a pessoa se sente em relação à comida e ao corpo.
- **Cuidados de conteúdo:** os sinais aparecem no nível do comportamento, sem detalhar métodos. O paciente simulado não estimula nem ensina comportamentos de risco, e o feedback (NS-051) explica a conduta esperada.
- **Decisão pendente da equipe:** como as etapas 3 e 4 funcionam neste perfil. Proposta: o estudante pode registrar o encaminhamento em vez do plano, e a rubrica valoriza essa escolha. A decisão está no card NS-071 (#85), que afeta o frontend (NS-042) e a rubrica (NS-049).

## Níveis de dificuldade

O nível muda **o comportamento do paciente**, não a doença. Os três níveis já existem no contrato da API (`facil`, `medio`, `dificil`).

| Dimensão | Fácil | Médio | Difícil |
|---|---|---|---|
| Informações omitidas, reveladas só diante da pergunta certa | 1 | 3 | 5 |
| Precisão do relato alimentar | relata porções e frequências corretamente | subestima porções de forma leve | subestima porções e "esquece" itens, mas corrige quando o estudante investiga |
| Postura | colaborativa | ambivalente: quer mudar, mas duvida que consiga | resistente: já tentou dietas antes, desconfia e questiona as orientações |
| Restrições de vida que o plano precisa respeitar | 1 (por exemplo, orçamento) | 2 | 3 (por exemplo, orçamento, turno de trabalho e aversões) |
| Forma de responder | respostas completas | respostas curtas; às vezes desvia do assunto | respostas vagas, que exigem perguntas de aprofundamento |

Limites que valem para todos os níveis:

- O paciente **nunca se contradiz** sobre fatos da ficha. Relato impreciso e informação omitida são previstos e ficam marcados na ficha, para que o juiz do eval os classifique como *omissão prevista*, e não como *contradição* (NS-017).
- O paciente difícil é resistente, **nunca hostil ou ofensivo**.
- O paciente nunca pede nem dá diagnóstico, prescrição ou números calculados.

## Diversidade e cuidado com estereótipos

Cada ficha sorteia ou define estas características **independentemente da condição clínica**, para que nenhuma combinação vire padrão:

| Característica | Variações previstas |
|---|---|
| Gênero | mulheres e homens em todos os perfis |
| Renda e orçamento para alimentação | baixo, médio e alto, em todos os perfis |
| Rotina | horário comercial, turno noturno, trabalho braçal, home office, aposentadoria, cuidado de familiar (dupla jornada) |
| Quem cozinha | o próprio paciente, outra pessoa da casa, ninguém (come fora) |
| Cultura alimentar | hábitos regionais do Espírito Santo e de outras regiões, por exemplo moqueca, torta capixaba, cuscuz, arroz com feijão diário |
| Preferências e restrições | aversões, vegetarianismo, restrições religiosas |

Lista de conferência na revisão de cada perfil e de cada ficha:

- [ ] Renda baixa não aparece associada a "não saber comer" ou a falta de informação.
- [ ] Excesso de peso não aparece associado a preguiça ou falta de força de vontade.
- [ ] A condição clínica não está ligada a gênero, raça ou região de forma caricata.
- [ ] Sotaque e linguagem regional não são usados como piada.
- [ ] Os nomes variam em origem e gênero.
- [ ] A dificuldade vem do comportamento do paciente, e não da condição social dele.

## O que o schema da ficha (NS-014) precisa comportar

Os perfis acima pedem estes grupos de campos. A divisão entre o que o paciente simulado vê e o que é gabarito segue a arquitetura: o paciente recebe a ficha **sem** o gabarito.

| Grupo | Campos | Quem vê |
|---|---|---|
| Identificação | `perfil_id`, `dificuldade`, nome, idade, gênero | paciente |
| Dados para o motor | peso, altura, nível de atividade física | paciente e motor |
| Restrições verificáveis | `sodio_max_mg`, `fibras_min_g_por_1000kcal`, `gordura_saturada_max_pct_vet`, `proteina_g_kg_min` e `proteina_g_kg_max` (todos opcionais), alimentos evitados, faixa de orçamento | motor |
| Vida e hábitos | rotina, quem cozinha, preferências, aversões, cultura alimentar, recordatório alimentar | paciente |
| Comportamento | postura, forma de responder, lista de imprecisões previstas no relato | paciente |
| Informações omitidas | lista de itens, cada um com a informação e a pergunta ou tema que a revela | paciente |
| Gabarito | conduta esperada (`plano` ou `encaminhamento`), sinais de alerta, o que a anamnese deveria descobrir | rubrica e eval, **nunca o paciente** |

A conferência final com o schema real fica como item do card, depois que a NS-014 for publicada.

## Referências

- BAUER, J. et al. Evidence-based recommendations for optimal dietary protein intake in older people: a position paper from the PROT-AGE Study Group. *Journal of the American Medical Directors Association*, v. 14, n. 8, p. 542-559, 2013.
- BARROSO, W. K. S. et al. Diretrizes Brasileiras de Hipertensão Arterial – 2020. *Arquivos Brasileiros de Cardiologia*, v. 116, n. 3, p. 516-658, 2021.
- BRASIL. Ministério da Saúde. *Guia alimentar para a população brasileira*. 2. ed. Brasília: Ministério da Saúde, 2014.
- RAMOS, S. et al. Terapia nutricional no pré-diabetes e no diabetes mellitus tipo 2. In: *Diretriz Oficial da Sociedade Brasileira de Diabetes*. 2023. DOI: 10.29327/5238993.2023-8.
- WORLD HEALTH ORGANIZATION. *Guideline: sugars intake for adults and children*. Geneva: WHO, 2015.
- WORLD HEALTH ORGANIZATION. *Guideline: sodium intake for adults and children*. Geneva: WHO, 2012.
- WORLD HEALTH ORGANIZATION. *Saturated fatty acid and trans-fatty acid intake for adults and children: WHO guideline*. Geneva: WHO, 2023.
