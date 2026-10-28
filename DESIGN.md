# Design do NutriSim

Identidade visual e componentes da interface do NutriSim. Este arquivo é a fonte das regras. Os valores dos tokens (cores, raios, sombra) ficam só no `frontend/src/app/globals.css`.

- **Vitrine visual (design system):** https://claude.ai/artifact/LyyG6Us3oibo3ad5YrhfZb. Só tokens, logos em SVG e previews ao vivo dos componentes; as regras ficam aqui.
- **Telas (canvas):** https://claude.ai/artifact/AXdcpqqgt6qN4LdSR4ZnqR. As telas do app em tamanho real, desktop e celular, com tema escuro e claro. Ao mudar um token no `globals.css`, atualize também o `tokens.json` da vitrine, que desenha as amostras.
- **Implementação:** tokens no `@theme` do Tailwind 4 (`frontend/src/app/globals.css`) e componentes React em `frontend/src/components/ui/`. O mapeamento está em [Tokens no Tailwind 4](#tokens-no-tailwind-4).

## Sumário

1. [Princípios](#princípios)
2. [Voz e conteúdo](#voz-e-conteúdo)
3. [Cores](#cores)
4. [Tipografia](#tipografia)
5. [Espaço, forma e sombra](#espaço-forma-e-sombra)
6. [Movimento](#movimento)
7. [Iconografia](#iconografia)
8. [Logo](#logo)
9. [Acessibilidade](#acessibilidade)
10. [Componentes](#componentes)
11. [Telas de referência](#telas-de-referência)
12. [Tokens no Tailwind 4](#tokens-no-tailwind-4)

## Princípios

A interface tem que passar rigor clínico com cara de ferramenta moderna: escura, precisa e sem enfeite. A referência de linguagem é o console do Neon (o app, não o site de marketing): conteúdo em preto puro dentro de uma moldura um tom acima, bordas finas, cantos quase retos, controles compactos, títulos pequenos com peso, três tons de texto, rótulos de seção em mono caixa-alta e um único acento usado como assinatura. O refinamento vem da densidade e da hierarquia por peso e tom, não de enfeite. O grid decorativo e as animações de vitrine do site ficaram de fora porque não cabem num app clínico.

### A regra que define o sistema

**A IA representa o paciente; o motor calcula a fisiologia.** A interface deixa essa divisão visível:

| Origem | Como aparece |
|---|---|
| **Motor** (kcal, gramas, GET, % de adequação) | Geist Mono, números tabulares, unidade junto: `127 kcal`, `50 g` |
| **IA** (ficha, paciente, feedback) | Badge `accent` com o ícone de brilho: "Gerado por IA", "Paciente simulado por IA" |
| **Fala do paciente** | Texto comum em Geist, no balão neutro |

Nunca coloque um número calculado dentro do balão do paciente.

## Voz e conteúdo

- Português do Brasil, frases curtas e voz ativa. Fale com o estudante como um preceptor: direto e sem infantilizar.
- Os botões dizem o que acontece: "Gerar paciente e iniciar", "Concluir e gerar simulação de adesão". Nunca use "OK" ou "Enviar" sem contexto.
- Use os termos da Nutrição como eles são: anamnese, GET, TACO, adesão, plano alimentar. Não traduza para "quiz" ou "dieta".
- A mensagem de erro diz como corrigir: "Informe uma quantidade maior que zero."
- Sem emoji, sem exclamação e sem superlativo.
- Números: unidade separada por espaço (`50 g`, `127 kcal`) e milhar separado por espaço fino (`1 850 kcal`).

## Cores

O tema **escuro é a base** e vem primeiro. O claro usa os mesmos nomes de token. O app segue o tema do sistema operacional. No escuro, os neutros são cinzas frios sobre preto puro; no claro, zinc.

O lima (`accent`) é o recurso mais escasso do sistema e funciona como assinatura. Ele só aparece no badge de IA, no anel de foco, no segmento atual da barra de progresso, na etapa atual, no hover de dois ícones (o de IA dentro de um botão e o do item da barra lateral) e no pontilhado das telas de passagem. Nunca vai no fundo de botão: o primário é preenchido em `fg`. Navegação ativa e aba ativa usam `fg`, nunca o lima. Os estados têm paleta própria e nunca usam o lima. Todo estado vem com ícone e texto, nunca só com cor.

### Neutros

| Token | Uso |
|---|---|
| `bg` | Fundo da página |
| `surface` | Cards, painéis, campos de formulário, balão do paciente |
| `surface-raised` | Balão do estudante, hover de botão fantasma, trilho da barra de adesão |
| `surface-hover` | Hover e item ativo da barra lateral. Visível sobre `chrome` e `bg` |
| `chrome` | Moldura do app: fundo da Sidebar, da Appbar e do cabeçalho de tabela |
| `line` | Bordas de 1px entre áreas e em cards. Separa sem sombra. É decorativa e não marca controles |
| `line-strong` | Borda de controles (input, select, botão secundário). Contraste de 3:1 sobre `bg`, `surface` e `surface-raised` |
| `fg` | Texto principal: títulos, item ativo, dado em destaque. Também o preenchimento do botão primário |
| `fg-secondary` | Texto de apoio: itens da lateral, descrições, valores da PropertyList |
| `fg-muted` | Rótulos, metadados, trilha, placeholders. 4.5:1 sobre `bg`, `surface`, `surface-raised` e `chrome` |
| `glow` | Brilho do acento a 3% no canto do conteúdo, só no escuro. Quase invisível de propósito |

São três tons de texto. A hierarquia vem do tom e do peso, não do tamanho: uma lista com tudo em `fg-muted` achata, e uma com tudo em `fg` grita.

### Acento (lima)

| Token | Uso |
|---|---|
| `accent` | Badge de IA, foco, segmento atual do progresso e etapa atual. Nunca em botão. Como texto, só sobre `bg`, `surface` ou `accent-soft` |
| `accent-hover` | Hover de um elemento lima interativo. O botão primário não usa |
| `accent-soft` | Fundo tingido atrás de texto `accent` |
| `accent-inverse` | O lima do tema oposto, para o ícone de IA sobre o primário (fundo `fg`): escuro no tema escuro, claro no claro |
| `on-accent` | Texto e ícone sobre preenchimento `accent` (número da etapa atual) |
| `focus` | Anel de foco do teclado |

O lima brilha no escuro. No claro ele escurece para manter o contraste, então nunca use o lima do tema escuro sobre fundo claro.

### Estados

| Token | Uso |
|---|---|
| `success` | Estado bom (adesão alta, meta atingida). É esmeralda, nunca o lima |
| `success-soft` | Fundo de badge e alerta de sucesso |
| `warning` | Atenção (adesão moderada, restrição perto do limite) |
| `warning-soft` | Fundo de badge e alerta de atenção |
| `danger` | Erro e estado crítico (adesão baixa, restrição violada) |
| `danger-soft` | Fundo de badge e alerta de erro |

O texto de estado vai sobre `bg`, `surface` ou o `-soft` correspondente.

## Tipografia

O sistema usa duas famílias, ambas do Google Fonts (no Next, via `next/font/google`). O logotipo é Space Grotesk, mas já vem convertido em path, então essa fonte não é carregada.

| Família | Token | Papel | Pesos |
|---|---|---|---|
| **Geist** | `sans` e `display` | Toda a interface, os títulos e o texto corrido. Só o `display-xl` da landing usa peso 400 com tracking bem negativo | 400, 500, 600 |
| **Geist Mono** | `mono` | Dados do motor, horários, metadados e os rótulos de seção (`eyebrow`) | 400, 500 |

Pilhas de fallback:

```css
--font-display: "Geist", system-ui, sans-serif;
--font-sans: "Geist", system-ui, sans-serif;
--font-mono: "Geist Mono", ui-monospace, "SFMono-Regular", monospace;
```

### Escala

| Estilo | Família | Tamanho / altura de linha | Peso | Tracking | Uso |
|---|---|---|---|---|---|
| `display-xl` | display | 56 / 63px | 400 | -0.04em | Título da landing, uma vez por página |
| `h1` | display | 28 / 34px | 500 | -0.02em | Título da página. Pode ter dois tons: a segunda frase em `fg-muted` |
| `h2` | display | 22 / 28px | 500 | -0.015em | Título da etapa e de seção grande |
| `h3` | sans | 18 / 26px | 600 | 0 | Título de card e de grupo |
| `body` | sans | 15 / 24px | 400 | 0 | Texto corrido e mensagens do chat |
| `body-sm` | sans | 13 / 20px | 400 | 0 | Ajuda de campo, legenda |
| `control` | sans | 14 / 20px | 500 | 0 | Botão padrão e aba |
| `label` | sans | 13 / 16px | 500 | 0 | Rótulo de campo e botão pequeno |
| `data-lg` | mono | 24 / 28px | 500 | 0 | Número de destaque do motor (GET, total do plano) |
| `data` | mono | 14 / 20px | 400 | 0 | Quantidades, nutrientes e porcentagens em linhas e tabelas |
| `eyebrow` | mono | 12 / 16px | 500 | 0.04em | Título de seção e de grupo, e rótulo técnico curto (método, fonte do dado), em caixa alta |

Os títulos de seção e de grupo ("Sessões recentes", "Em andamento", "Queixa principal") são `eyebrow`: Geist Mono em caixa alta e `fg-muted`. Legenda, trilha e rótulo de campo continuam em Geist. Só o `eyebrow` usa caixa alta.

O texto da interface tem tracking de -0.01em, definido no `body`; o `eyebrow` abre para 0.04em. No celular, o `h1` cai para 24/30px. Num app, título pequeno com peso passa mais precisão que título grande e leve, que é linguagem de landing.

Todo número do motor usa `font-variant-numeric: tabular-nums` para alinhar em colunas. O texto do corpo da página é `body` (15/24) sobre `bg` em `fg`.

## Espaço, forma e sombra

### Espaçamento

A base é de 4px, a mesma escala do Tailwind (`space-4` = `p-4`).

| Token | Valor | Uso |
|---|---|---|
| `space-1` | 4px | Entre ícone e texto colados |
| `space-2` | 8px | Entre ícone e rótulo no botão; entre itens de lista |
| `space-3` | 12px | Padding de campos; gap entre botões |
| `space-4` | 16px | Padding de botão; gap padrão entre elementos |
| `space-6` | 24px | Padding de card; gap entre grupos |
| `space-8` | 32px | Entre seções dentro de uma tela |
| `space-12` | 48px | Margem de página no desktop |
| `space-16` | 64px | Entre blocos da landing |

O card padrão tem `space-6` de padding, `space-4` entre elementos e `space-8` entre seções.

### Raios

| Token | Uso |
|---|---|
| `radius-md` (6px) | Botões, inputs, selects, itens de menu e alertas |
| `radius-lg` (8px) | Cards, painéis, listas, cartões de opção e o canto da moldura do conteúdo |
| `radius-xl` (20px) | Composer do chat, que cresce com o texto |
| `radius-pill` | Badges, chips e avatares |

Controle e container são quase retos; a pílula fica só no que é rótulo (badge) ou pessoa (avatar). O balão do chat é a exceção, com 14px e o canto do rabicho em 4px.

### Borda, não sombra

As áreas se separam pela borda `line` (1px) e pelo contraste de `surface` sobre `bg`. Os controles usam `line-strong`. A única sombra do sistema é a de camadas flutuantes:

| Token | Uso |
|---|---|
| `shadow-overlay` | Menus, popovers e diálogos. Nunca em cards |

### Pontilhado

Malha de pontos lima que some a partir de dois cantos opostos. É a marca nas telas **de passagem**, com pouco conteúdo e sem dado clínico: login, estado vazio, espera da IA ("Gerando paciente…") e erro/404. Nunca em tela de trabalho (anamnese, plano, cenários, feedback, tabelas); lá o `glow` faz esse papel.

| Parte | Especificação |
|---|---|
| Pontos | `radial-gradient(circle, var(--accent) 1.2px, transparent 1.8px)` em grade de 7 × 7px |
| Máscara | `radial-gradient(120% 70% at 0 0, #000, transparent 60%)` + `radial-gradient(110% 60% at 100% 100%, #000, transparent 60%)` |
| Opacidade | .5 no escuro, .28 no claro (o lima escurece e pesaria no branco) |
| Camada | `position: absolute; inset: 0; z-index: -1; pointer-events: none`, com `aria-hidden`; o container tem `overflow: hidden` e `isolation: isolate` |

## Movimento

O movimento se limita ao necessário: transições de 150ms em hover (cor de fundo, borda e texto), os três pontos enquanto o paciente pensa e o cursor piscando no streaming do chat. Tudo para com `prefers-reduced-motion: reduce`.

## Iconografia

- Ícones lineares no estilo Lucide: grade de 24, traço de 1,5px, pontas e junções arredondadas, cor `currentColor`.
- Tamanho de 16px em botões e abas e de 12px em badges.
- O ícone só apoia o texto. Botão só de ícone exige `aria-label`.
- Na implementação, use `lucide-react` com `strokeWidth={1.5}`.

| Ícone | Lucide | Onde |
|---|---|---|
| Brilho | `Sparkle` | Badge de IA, botão "Gerar…" |
| Chevron para baixo | `ChevronDown` | Select |
| Chevron para a esquerda | `ChevronLeft` | Voltar |
| Seta para cima | `ArrowUp` | Enviar, no composer do chat |
| Seta para a direita | `ArrowRight` | Depois do rótulo da ação que avança a etapa |
| Lápis | `Pencil` | Editar refeição |
| Mais | `Plus` | Adicionar refeição, Nova sessão |
| Info | `Info` | Dica em formulário |
| Info pequeno | `Info` (14px) | InfoHint, ao lado de um termo técnico |
| Copiar | `Copy` | Copiar ID ou código num campo só de leitura |
| Reticências | `EllipsisVertical` | Ações secundárias da linha de tabela |
| Lupa | `Search` | Busca da tabela |
| Check, triângulo, círculo | `Check`, `TriangleAlert`, `CircleAlert` | Badges de sucesso, atenção e erro; etapa concluída |
| Casa, relógio | `House`, `History` | Início e Histórico na barra lateral |
| Estetoscópio | `Stethoscope` | Sessão em andamento na barra lateral |
| Painel à esquerda | `PanelLeft` | Recolher e expandir a barra lateral |
| Painel à direita | `PanelRight` | Abrir e fechar o painel da consulta |
| Menu, X | `Menu`, `X` | Abrir a gaveta no mobile; fechar gaveta e painel |
| Lua, sol | `Moon`, `Sun` | Trocar o tema |
| Sair | `LogOut` | Sair da conta |

## Logo

O símbolo é um balão de fala com uma folha em lima. A folha é um furo real, então o fundo aparece através dela. O logotipo "**Nutri**Sim" é Space Grotesk (Nutri 700, Sim 400), já convertido em path.

| Arquivo | Quando usar |
|---|---|
| `nutrisim-escuro.svg` | Fundo escuro (símbolo `#A3E635`, texto `#F5F5F4`). É a versão padrão |
| `nutrisim-claro.svg` | Fundo claro (símbolo `#4D7C0F`, texto `#0C0A09`) |
| `nutrisim-mono-preto.svg` / `nutrisim-mono-branco.svg` | Uma cor só, para impressão e fundos coloridos |
| `nutrisim-simbolo-escuro.svg` / `nutrisim-simbolo-claro.svg` | Só o símbolo, para avatar e espaços quadrados |

- **Área de respiro:** a altura do rabicho do balão, em volta da logo.
- **Altura mínima:** 16px para o símbolo. Na barra lateral e na Appbar, a logo completa tem 20px.
- O favicon (`app/icon.svg`) troca de cor sozinho com o tema.
- Não recolorir, não trocar a fonte e não aplicar o lima sobre fundo claro.

Os SVGs estão na vitrine, no grupo Logos.

## Acessibilidade

- O texto tem contraste de 4.5:1 sobre o fundo em que é usado, nos dois temas. Bordas de controle, foco e ícones têm 3:1.
- Alvo de toque de 44px no celular (botão, aba, campo). No desktop, botão e campo têm 36px e o `--sm` 32px, acima dos 24px do AA da WCAG 2.2.
- Foco visível em tudo: anel de 2px em `focus`, afastado 2px do elemento. Nos campos o afastamento é 0 e a borda some.
- Chat como `role="log"`, abas no padrão tablist e barra de adesão como `role="meter"`.
- Estado nunca é só cor: sempre ícone e texto.
- Todo campo tem `<label>` visível. Quando o rótulo não pode aparecer (composer do chat), ele fica escondido só visualmente, mas continua no HTML.

## Componentes

Todos os componentes são HTML e CSS com classes `ns-*`, sem JS próprio. Os valores de cada um usam os tokens acima. No app eles viram componentes React em `components/ui/`.

### Button

Botão de ação, retangular com `radius-md`. `primary` é para a única ação principal da tela, `secondary` para as demais e `ghost` para ações de baixo peso.

**Anatomia:** `button.ns-btn` (ou `a.ns-btn`) com ícone opcional e rótulo.

| Variante | Fundo | Texto | Borda | Hover |
|---|---|---|---|---|
| `--primary` | `fg` (branco no escuro, preto no claro) | `bg` | transparente | fundo `fg` a 80% sobre `bg` |
| `--secondary` | transparente | `fg` | `line-strong` | borda `fg` |
| `--ghost` | transparente | `fg-muted` | transparente | fundo `surface-raised`, texto `fg` |

| Tamanho | Altura | Padding horizontal | Fonte |
|---|---|---|---|
| padrão | 36px (44px abaixo de 768px) | `space-4` (16px) | Geist 500, 14px |
| `--sm` | 32px | `space-3` (12px) | Geist 500, 13px |
| `--icon` | quadrado da altura do tamanho | 0 | só ícone |

- **Geral:** raio `radius-md`, gap de `space-2` entre ícone (16px) e rótulo, `white-space: nowrap` e transição de 150ms.
- **Disabled:** opacidade .45 e `cursor: not-allowed`.
- **Ícone de IA (`Sparkle`) no botão:** fica lima no hover do botão (`accent`; no primário, `accent-inverse`). Os outros ícones de botão seguem a cor do texto.
- **Um primário por tela.** Se dois botões pedem destaque, um deles é secundário.
- **A lima não vai em botão.** Ela é a assinatura (IA, foco, progresso), e o primário se destaca pelo contraste do `fg`.
- `--sm` só em barras densas no desktop.
- O rótulo usa verbo e diz o que acontece. Botão só de ícone exige `aria-label`.
- Use `<button>` ou `<a>` reais, nunca `div` clicável.

### Input e Textarea

Campo de texto com rótulo visível, ajuda opcional e mensagem de erro. A variante `ns-textarea` serve para anotações.

**Anatomia:** `div.ns-field` > `label.ns-label` + `input.ns-input` (ou `textarea.ns-textarea`) + `p.ns-help` ou `p.ns-error`.

| Parte | Especificação |
|---|---|
| Campo | `ns-field`: coluna com gap de 6px |
| Rótulo | `label` (Geist 500, 13/16px), cor `fg` |
| Caixa | altura 36px (44px abaixo de 768px), padding horizontal `space-3`, borda 1px `line-strong`, raio `radius-md`, fundo `surface`, texto `fg` em `body` (15/24px) |
| Placeholder | `fg-muted` |
| Ajuda | `body-sm` (13/20px), `fg-muted` |
| Erro | `body-sm`, `danger`, ícone de 16px com gap `space-1` |
| Textarea | altura mínima 96px, padding `space-3`, redimensiona só na vertical |

| Estado | Visual |
|---|---|
| hover | borda `fg-muted` |
| foco | anel de 2px `focus` com afastamento 0, borda transparente |
| erro | `ns-field--error`: borda `danger` no input, select ou textarea |

- Sempre `<label for>` visível. O placeholder é exemplo, nunca o rótulo.
- **Só leitura** (`readonly`, dado gerado pela IA ou ID): fundo `surface-raised`, borda `line`, texto `fg-secondary`. O fundo cheio diz "não editável" antes de a pessoa tentar. ID e código vão em Geist Mono com botão de copiar (ghost `--sm --icon`, `Copy`) dentro da caixa, à direita.
- Valores numéricos (peso, gramas, kcal) usam `ns-num` (Geist Mono, tabular) e o `inputmode` adequado.
- No erro, coloque `aria-invalid="true"` e um `aria-describedby` que aponte para o `ns-error`. A mensagem diz como corrigir.

### Select

Lista de opções sobre o `<select>` nativo, com a mesma caixa do Input e um chevron desenhado por cima.

**Anatomia:** `div.ns-select-wrap` (relativo) > `select.ns-select` + `svg.ns-icon` (chevron).

- **Caixa:** igual ao Input, com `appearance: none`, `padding-right: 40px` e `cursor: pointer`.
- **Chevron:** 16px, cor `fg-muted`, posição absoluta (`right: space-3`, centralizado na vertical) e `pointer-events: none`.
- **Hover e foco:** iguais ao Input.
- É nativo de propósito: teclado, leitor de tela e o seletor do celular vêm de graça. Só troque por um menu próprio se precisar de busca (ex.: alimentos da TACO).
- Os filtros do histórico (Patologia, Dificuldade, Data) usam este mesmo componente.
- Com até 3 opções em que a descrição ajuda a decidir, prefira o ChoiceCard.

### ChoiceCard

Grupo de rádios em cartões, para escolhas curtas em que a descrição de cada opção fica visível para comparar. Hoje é a dificuldade do paciente (Fácil, Média, Difícil).

**Anatomia:** `fieldset.ns-choice` > `legend.ns-label` + `div.ns-choice__grid` > `label.ns-choice__item` > `input[type=radio]` + `span.ns-choice__title` + `span.ns-choice__text`.

| Parte | Especificação |
|---|---|
| Grade | 3 colunas iguais com gap `space-3`; uma coluna abaixo de 768px |
| Cartão | coluna com gap `space-1`, padding `14px space-4`, borda 1px `line-strong`, raio `radius-lg` |
| Título | Geist 500 14/20px |
| Descrição | `body-sm`, `fg-muted` |
| hover | borda `fg-muted` |
| escolhido (`:has(:checked)`) | borda `fg` de 2px (borda + `inset` de 1px) e fundo `surface-raised` |
| foco | anel de 2px `focus` em volta do cartão, afastado 2px |

- O rádio nativo continua dentro do cartão, invisível (`opacity: 0`), então as setas do teclado e o leitor de tela funcionam como num grupo de rádios comum.
- O escolhido muda borda e fundo, não só a cor: dá para distinguir em escala de cinza.

### Tabs

Abas no padrão ARIA de tablist, com navegação pelas setas. Hoje aparecem no painel da consulta (Conversa e Anotações).

**Anatomia:** `div.ns-tabs[role=tablist]` > `button.ns-tab[role=tab]`. Os painéis (`role="tabpanel"`) ficam com o consumidor, ligados à aba por `aria-controls`.

| Parte | Especificação |
|---|---|
| Lista | flex com gap `space-1`, borda inferior 1px `line`, rolagem horizontal |
| Aba | altura 44px, padding `0 space-4`, Geist 500 14px, cor `fg-muted`, sublinhado de 2px transparente sobreposto à borda (`margin-bottom: -1px`) |
| hover | texto `fg` |
| ativa (`aria-selected="true"`) | texto `fg` e sublinhado de 2px em `fg` |

- A aba ativa usa `fg`, não lima: o lima fica para a assinatura (IA, foco, progresso).
- Aba inativa recebe `tabindex="-1"`, e as setas movem o foco.
- Se não couber, a lista rola na horizontal. Nunca quebre em duas linhas.

### Card

Superfície para agrupar um caso clínico, um atendimento do histórico ou um bloco de funcionalidade.

**Anatomia:** `div.ns-card` > `span.ns-eyebrow` + `h3.ns-card__title` + `p.ns-card__text` + `div.ns-card__foot` (badges).

| Parte | Especificação |
|---|---|
| Caixa | coluna com gap `space-3`, padding `space-6`, borda 1px `line`, raio `radius-lg`, fundo `surface` |
| Título | `h3` (Geist 600, 18/26px) |
| Texto | `body`, `fg-muted` |
| Rodapé | flex com wrap e gap `space-2` |
| `--link` | o card inteiro é um `<a>`. No hover, a borda vira `line-strong` |

- Não tem sombra: a separação vem da borda e do contraste `surface` sobre `bg`.
- A ordem interna é eyebrow (fonte do dado, data), título, texto e rodapé com badges.
- Não aninhe cards. Dentro de um card, separe com divisórias de 1px `line`.

### Badge

Rótulo curto em pílula para categoria (neutro), origem por IA (`accent`) ou estado (`success`, `warning`, `danger`).

**Anatomia:** `span.ns-badge` com ícone opcional de 12px e texto.

| Parte | Especificação |
|---|---|
| Caixa | altura 24px, padding `0 10px`, gap 6px, raio `radius-pill`, Geist 500 12px |

| Variante | Fundo | Texto | Borda | Ícone |
|---|---|---|---|---|
| neutro | transparente | `fg-muted` | `line-strong` | nenhum |
| `--accent` | `accent-soft` | `accent` | transparente | brilho |
| `--success` | `success-soft` | `success` | transparente | check |
| `--warning` | `warning-soft` | `warning` | transparente | triângulo |
| `--danger` | `danger-soft` | `danger` | transparente | círculo |

- `--accent` só marca o que a IA gerou (ficha, paciente, feedback), nunca um estado.
- Estado sempre com ícone e texto.
- O texto tem uma ou duas palavras. Badge não é botão.

### ChatBubble e Composer

Mensagens da anamnese. O paciente simulado fica à esquerda e o estudante à direita. Enquanto o paciente pensa aparecem três pontos e, durante o streaming, um cursor.

**Anatomia:**

```text
div.ns-chat[role=log]
└── div.ns-msg.ns-msg--patient | .ns-msg--student
    ├── span.ns-avatar            (só paciente)
    └── div.ns-msg__body
        ├── div.ns-bubble
        └── span.ns-msg__meta
form.ns-composer
├── label (escondido só visualmente)
├── textarea
└── button.ns-send (Enviar)
```

| Parte | Especificação |
|---|---|
| Chat | coluna com gap `space-4` |
| Mensagem | largura máxima de 80% da coluna, gap `space-3` entre avatar e corpo, gap `space-2` entre balão e meta |
| Avatar | 32px, raio `radius-pill`, borda `line`, fundo `surface`, iniciais em Geist Mono 500 12px `fg-muted`, sem cor por pessoa |
| Balão | padding `10px 14px`, raio de 14px, `body` (15/24px), quebra de palavra longa |
| Balão do paciente | fundo `surface`, borda `line`, canto inferior esquerdo com raio de 4px |
| Balão do estudante | fundo `surface-raised`, sem borda, canto inferior direito com raio de 4px |
| Meta | Geist Mono 12/16px, `fg-muted` (hora; "João · 09:12") |
| Pensando | `ns-typing` no balão: três pontos de 6px em `fg-muted` que sobem em sequência; meta "João está digitando…" |
| Cursor | 8 × 18px em `fg`, pisca a cada 1s (`steps(1)`) |
| Composer | pílula de raio `radius-xl`, borda 1px `line-strong`, fundo `surface`, padding `6px 6px 6px 18px`; o textarea cresce sozinho até 144px; no foco, anel `focus` e borda transparente |
| Enviar | `ns-send`: círculo de 36px em `fg` com `ArrowUp` em `bg`; opacidade .3 quando desativado |

- Os balões não têm lima. A conversa é neutra.
- Enquanto o paciente pensa, o balão tem `ns-typing` e `aria-busy="true"`. Durante o streaming, o balão tem `ns-cursor` no fim do texto, e a meta diz "João está respondendo…". Com `prefers-reduced-motion`, os pontos e o cursor param.
- O contêiner é `role="log"` para o leitor de tela anunciar as mensagens novas.
- Enter envia e Shift+Enter quebra a linha, com essa dica em `body-sm` embaixo do composer. O Enviar fica desativado com o campo vazio ou enquanto o paciente responde.
- O primário da anamnese é "Montar o plano", no cabeçalho da sessão.

### AdherenceBar

Barra que compara o cenário realista com a meta do plano para um nutriente. A marca vertical é a meta (adesão ideal = 100%).

**Anatomia:**

```text
div.ns-meter (.ns-meter--warning | --danger)
├── div.ns-meter__head   → span.ns-meter__label + Badge de estado
├── div.ns-meter__track[role=meter]
│   ├── div.ns-meter__fill  (width = valor ÷ 120)
│   └── div.ns-meter__mark  (left: 83,3%)
└── div.ns-meter__foot   → "realista 65%" · "meta 100%"
```

| Parte | Especificação |
|---|---|
| Bloco | grid com gap `space-2` |
| Rótulo | Geist 500 13/16px |
| Trilho | altura 8px, raio `radius-pill`, fundo `surface-raised` |
| Preenchimento | cor da faixa, mesmo raio do trilho |
| Marca da meta | 2px de largura, 4px além do trilho em cima e embaixo, cor `fg` |
| Rodapé | Geist Mono 12/16px, `fg-muted` |

| Faixa | Valor | Cor | Badge |
|---|---|---|---|
| Alta | ≥ 80% | `success` (padrão) | "Alta" |
| Moderada | 50–79% | `warning` (`--warning`) | "Moderada" |
| Baixa | < 50% | `danger` (`--danger`) | "Baixa" |

- A escala vai de 0 a 120% para mostrar excesso.
- Os números são mono porque vêm do motor determinístico, não da IA.
- Acessibilidade: `role="meter"`, `aria-valuemin="0"`, `aria-valuemax="120"`, `aria-valuenow` e um `aria-valuetext` em frase ("65% da meta no cenário realista").
- O consumidor fornece valor, meta e rótulo. A faixa de cor sai do valor.

### MealItem

Uma refeição do plano alimentar: título com horário, alimentos com quantidade e energia, total no rodapé e ação de editar.

**Anatomia:**

```text
section.ns-meal
├── div.ns-meal__head → h3.ns-meal__title (+ span.ns-meal__time) + Button ghost sm "Editar"
├── ul.ns-meal__list  → li.ns-meal__food: nome · quantidade · kcal
└── div.ns-meal__total → "Total da refeição" · kcal
```

| Parte | Especificação |
|---|---|
| Caixa | borda 1px `line`, raio `radius-lg`, fundo `surface` |
| Cabeçalho | padding `space-2 space-2 space-2 space-4`, borda inferior `line` |
| Título | Geist 600 15/24px; horário em Geist Mono 13/20px `fg-muted`, com `space-2` à esquerda |
| Linha de alimento | grid `1fr 64px 80px`, gap `space-4`, padding `6px space-4`; quantidade e kcal alinhadas à direita em Geist Mono 14/20px tabular `fg-muted` |
| Total | grid `1fr 80px`, padding `space-3 space-4`, borda superior `line`, rótulo Geist 500 13px, valor Geist Mono 500 14px |

- As colunas de quantidade e kcal são fixas e alinhadas à direita, para comparar de cima a baixo.
- A IA nunca escreve estes números: eles vêm da TACO pelo motor.
- A unidade vai junto do número (`50 g`, `127 kcal`), e o milhar é separado por espaço fino.
- "Editar" é um botão ghost pequeno. "Adicionar refeição" fica fora do item, como botão secundário.

### Alert

Mensagem de estado dentro da tela: erro de carregamento, aviso ou dica de formulário.

**Anatomia:** `div.ns-alert` (`--info | --success | --warning | --danger`) > `svg.ns-icon` + `div.ns-alert__body` > `p.ns-alert__title` (opcional) + texto + `button.ns-alert__action` (opcional).

| Parte | Especificação |
|---|---|
| Caixa | flex com gap `space-2`, padding `space-3 space-4`, raio `radius-md`, `body-sm` (13/20px) |
| Ícone | 16px, obrigatório, alinhado à primeira linha |
| Título | Geist 600 14/20px |
| Ação | botão de texto sublinhado, Geist 500 13/20px, na cor do alerta |

| Variante | Fundo | Texto | Borda | Ícone |
|---|---|---|---|---|
| `--info` | transparente | `fg-muted` | `line` | `Info` em `fg` |
| `--success` | `success-soft` | `success` | transparente | `Check` |
| `--warning` | `warning-soft` | `warning` | transparente | `TriangleAlert` |
| `--danger` | `danger-soft` | `danger` | transparente | `CircleAlert` |

- Estado sempre com ícone e texto.
- A mensagem de erro diz o que fazer, e a ação ("Tentar de novo") resolve ali mesmo quando dá.
- `--info` é a dica de formulário. Não use alerta para conteúdo que cabe num `ns-help` ou que o texto da página já diz.

### Dialog

Confirmação antes de uma ação que não se desfaz, como encerrar a anamnese.

**Anatomia:** `div.ns-dialog-scrim` > `div.ns-dialog[role=dialog]` > `h2.ns-dialog__title` + `p.ns-dialog__text` + `div.ns-dialog__actions`.

| Parte | Especificação |
|---|---|
| Fundo | preto a 60% sobre a tela, com a caixa centralizada |
| Caixa | largura máxima de 440px, padding `space-6`, gap `space-3`, borda `line`, raio `radius-lg`, fundo `surface`, `shadow-overlay` |
| Título | Geist 600 18/26px, a pergunta ("Encerrar a anamnese?") |
| Texto | `body`, `fg-muted`: o que acontece depois |
| Ações | à direita, gap `space-2`: secundário para ficar ("Continuar conversando") e primário para seguir ("Encerrar e montar o plano"), ambos `--sm` |

- No app, use o `<dialog>` nativo com `showModal()`: ele prende o foco, fecha no Esc e devolve o foco ao botão que o abriu.
- O título e o texto ligam o diálogo por `aria-labelledby` e `aria-describedby`.

### Sidebar

Navegação principal do app, ao lado da Appbar. Fica expandida nas páginas comuns, recolhida dentro da sessão e vira gaveta no celular.

**Anatomia:**

```text
aside.ns-sidebar (.ns-sidebar--collapsed)
├── div.ns-sidebar__top       → logo de 20px (link para o início); na gaveta, + botão Fechar
└── div.ns-sidebar__body
    ├── a.ns-btn--secondary.ns-btn--sm.ns-sidebar__new   "Nova sessão"
    ├── nav.ns-sidebar__nav   → a.ns-navitem: Início, Histórico
    └── div.ns-sidebar__group → span.ns-sidebar__heading "Em andamento" + a.ns-navitem--session
```

| Parte | Especificação |
|---|---|
| Barra | 240px, fundo `chrome`, sem borda: a separação vem da moldura do conteúdo |
| Topo | altura 56px (alinha com a Appbar), padding esquerdo 20px; logo de 20px |
| Corpo | coluna com gap `space-8` entre os grupos, padding `20px space-3` |
| Nova sessão | botão secundário `--sm` de largura total, ícone `Plus`; na tela de nova sessão, `aria-current="page"` e fundo `surface-raised` |
| Título de grupo | `eyebrow` em 11/16px: Geist Mono 500, caixa alta, `fg-muted` ("EM ANDAMENTO") |
| Item | altura mínima 32px, padding `0 10px`, gap 10px, raio `radius-md`, Geist 400 14/20px, `fg-secondary` |
| hover | fundo `surface-hover`, texto `fg` e ícone `accent` |
| ativo (`aria-current="page"`) | fundo `surface-hover`, texto `fg`, peso 500 |
| Sessão em andamento | ícone `Stethoscope`, nome do paciente e a etapa em Geist 12/16px `fg-muted` ("Etapa 3 de 5 · Plano alimentar") |
| Recolhida (`--collapsed`) | 64px, só ícones em botões de 40px, logo vira o símbolo |
| Gaveta (mobile) | `dialog.ns-drawer`: 280px, à esquerda, `shadow-overlay`, fundo atrás em preto a 60%; itens com 44px |

| Largura da tela | Comportamento |
|---|---|
| a partir de 1024px | expandida nas páginas comuns, recolhida nas telas da sessão |
| 768 a 1023px | sempre recolhida |
| abaixo de 768px | some; a Appbar ganha o botão de menu que abre a gaveta |

- O item ativo usa `fg` sobre `surface-hover`, nunca o lima. "Nova sessão" é secundário para não brigar com o primário da tela.
- O botão de recolher fica na Appbar (`PanelLeft`), com `aria-expanded` e `aria-controls`, e troca o `aria-label` entre "Recolher menu" e "Expandir menu". O app guarda a escolha da pessoa.
- Recolhida, os rótulos saem só da vista e continuam no HTML, e cada item ganha `title` com o rótulo.
- A gaveta é um `<dialog>` aberto com `showModal()`: o foco fica preso dentro dela, Esc fecha e o fundo fica inerte sem JS próprio. Ao fechar, o foco volta ao botão de menu.
- Só a sessão em andamento mais recente aparece. As outras ficam no Histórico.
- Tema e conta ficam na Appbar, não aqui.

### Appbar

Barra do topo, sempre visível ao lado da Sidebar: onde a pessoa está, à esquerda, e tema e conta, à direita.

**Anatomia:** `header.ns-appbar` > botão Recolher (ghost `--sm --icon`, `PanelLeft`) + `nav[aria-label="Trilha"]` > `ol.ns-crumbs` + `div.ns-appbar__end` > botão de tema (ghost `--sm --icon`) + `button.ns-avatar-btn`. No celular: botão Menu (ghost `--icon`) + logo de 20px + tema + conta.

| Parte | Especificação |
|---|---|
| Barra | altura 56px, padding `0 space-4 0 space-3`, fundo `chrome`, sem borda |
| Trilha | Geist 400 14/20px `fg-muted`, separador "/" em `line-strong`, item atual em `fg` com `aria-current="page"` |
| Tema | `Moon` no escuro ("Usar tema claro"), `Sun` no claro ("Usar tema escuro") |
| Conta | `ns-avatar-btn` de 32px com avatar de 28px e `aria-haspopup="menu"`; o menu tem Perfil e Sair |
| Celular | padding `0 space-2`, botões de 44px, sem trilha |

- A trilha diz onde a pessoa está: "Início / Nova sessão" numa página comum e "Início / João, 45 anos" na sessão. No Início ela some, porque o título já diz onde a pessoa está.
- A ação da etapa não vai na Appbar. Ela fica no cabeçalho da sessão.

### Stepper

Indicador das 5 etapas da sessão (Caso, Anamnese, Plano alimentar, Cenários, Retorno e feedback), no cabeçalho de toda tela da sessão.

**Anatomia:** `nav[aria-label="Etapas da sessão"]` > `ol.ns-steps` > `li.ns-step` (`--done` | `aria-current="step"`) > `a` ou `span.ns-step__item` > `span.ns-step__dot` + rótulo. No mobile, `details.ns-steps-compact` > `summary` (texto, chevron, `ns-progress`) + a mesma lista em `ns-steps--vertical`.

| Parte | Especificação |
|---|---|
| Lista | flex com gap `space-2`; entre as etapas, um traço de 24 × 1px em `line-strong` |
| Rótulo | Geist 500 13/20px, `fg-muted` |
| Círculo | 24px, borda 1px `line`, número em Geist Mono 500 12px |
| Concluída (`--done`) | círculo com borda `line-strong` e `Check` de 12px em `fg`; é um link para rever a etapa |
| Atual (`aria-current="step"`) | círculo cheio em `accent` com o número em `on-accent`; rótulo em `fg` |
| Futura | círculo com borda `line` e número em `fg-muted`; não é link |
| Compacto (mobile) | `summary` com 44px de altura mínima e borda inferior `line`: texto Geist 14/20px `fg-muted` "Etapa 3 de 5 · Plano alimentar", chevron e barra de 5 segmentos de 4px (concluída `line-strong`, atual `accent`, futura `surface-raised`) |

- A etapa atual é o lugar do lima nas etapas: marca onde a pessoa está sem competir com o primário, que é `fg`.
- A etapa concluída abre em modo leitura. A futura fica desativada até o estudante chegar nela.
- A concluída leva o texto "(concluída)" só para o leitor de tela (`ns-sr`), porque o check sozinho não diz nada.
- A barra de segmentos é decorativa (`aria-hidden`). Quem informa a etapa é o texto do resumo.
- Ao abrir uma sessão em andamento, o app leva direto à etapa atual.

### SidePanel

Painel da consulta à direita: guarda a conversa e as anotações para o estudante consultar nas etapas seguintes.

**Anatomia:** `aside.ns-panel` > `div.ns-tabs` (Conversa, Anotações) + `button.ns-panel__close` + `div.ns-panel__body[role=tabpanel]` + `div.ns-panel__foot`. Na anamnese, sem abas: `div.ns-panel__bar` ("Anotações" + fechar) no lugar delas. Fechado, sobra `nav.ns-panel-rail`.

| Parte | Especificação |
|---|---|
| Painel | 380px, borda esquerda `line`, fundo `bg` |
| Abas | Tabs com ícone: `MessageSquare` em Conversa e `NotebookPen` em Anotações; padding direito de 52px para o botão de fechar (ghost `--sm --icon`, `X`) |
| Corpo | rola sozinho, padding 20px, gap `space-3` |
| Conversa | badge "Paciente simulado por IA" no topo + ChatBubbles sem Composer, balão em 14/20px e largura máxima de 92% |
| Anotações | Textarea que ocupa a altura do corpo (mínimo 240px), com rótulo escondido só visualmente |
| Rodapé | Geist 12/16px `fg-muted`, borda superior `line`: "Salvas neste navegador às 09:14" |
| Faixa (fechado) | `ns-panel-rail`: 52px, borda esquerda `line`, um botão ghost `--sm --icon` por aba, com o mesmo ícone dela |

| Etapa | Conteúdo |
|---|---|
| Anamnese | só Anotações (a conversa já é o conteúdo principal) |
| Plano, Cenários, Retorno | abas Conversa (somente leitura) e Anotações (editável) |

- Fecha pelo X e abre pela faixa: cada ícone da faixa abre o painel direto na sua aba (`aria-label` "Abrir conversa" e "Abrir anotações", com `title`). Ao fechar, o foco vai para o ícone da aba que estava aberta.
- Não há botão do painel no cabeçalho da sessão: a faixa é o único jeito de abrir.
- Abaixo de 1024px vira gaveta à direita, e no celular ocupa a tela toda, aberta pelos dois ícones ao lado do título da etapa.
- As anotações salvam sozinhas, e o rodapé diz quando foi a última vez.

### PropertyList

Pares de rótulo e valor, em grupos que recolhem. É a ficha do paciente: idade, sexo, peso, altura, IMC, diagnóstico, atividade.

**Anatomia:** `section.ns-props` > `details.ns-props__group[open]` > `summary` (título + `ChevronDown`) + `dl` > (`dt` + `dd`)…

| Parte | Especificação |
|---|---|
| Grupo | padding `space-4 0`, borda inferior `line`; o último sem borda |
| Título do grupo | Geist 500 15/24px, `fg`, chevron de 16px em `fg-muted` que gira 180° fechado |
| Linha | grade `112px 1fr`, gap `space-3`, altura mínima 26px, Geist 13/20px |
| Rótulo (`dt`) | `fg-muted` |
| Valor (`dd`) | `fg-secondary`; número do motor em `ns-num`; link no estilo `ns-link` |

- Sem card: os grupos se separam só pela divisória.
- `details`/`summary` nativos: abrir e fechar funciona no teclado e no leitor de tela sem JS.
- O valor que a IA gerou não leva badge por linha. O badge de IA vai uma vez, no título do bloco.

### Table

Lista de registros com colunas: o Histórico e a busca na TACO.

**Anatomia:** `div.ns-table-head` (`h2` com a contagem + busca) + `table.ns-table` > `thead` + `tbody` > `tr` > `td`…

| Parte | Especificação |
|---|---|
| Título | `h3` com a contagem no texto: "12 sessões" |
| Busca | Input de largura total com `Search` de 16px à esquerda, logo abaixo do título, gap `space-3` |
| Cabeçalho (`th`) | fundo `chrome`, Geist 600 13/20px, `fg`, padding `space-3 space-4`, alinhado à esquerda (número à direita) |
| Linha | altura 46px, borda inferior `line`, Geist 14/20px; a primeira coluna em 500 `fg`, as demais em `fg-secondary` |
| Número | `ns-num`, alinhado à direita |
| Ação da linha | ghost `--sm --icon` com `EllipsisVertical` na última coluna, `aria-label` com o nome da linha |
| hover (linha que é link) | fundo `surface-hover` |

- O `thead` aparece sempre, inclusive carregando: a página não pula quando os dados chegam.
- Sem resultado na busca: uma linha só, centralizada em `fg-muted`, dizendo o que buscar ("Nenhuma sessão com \"Maria\". Busque pelo nome do paciente.").
- Abaixo de 768px a tabela vira lista: cada linha é um bloco com a primeira coluna em cima e as outras em `body-sm`.

### StatStrip

Faixa de números do motor lado a lado. É o resumo do plano: kcal, proteína, carboidrato e gordura contra a meta.

**Anatomia:** `div.ns-stats` > `dl.ns-stats__grid` > `div` > (`dt` + `dd`)… + `p.ns-stats__note`.

| Parte | Especificação |
|---|---|
| Caixa | Card com padding `space-6` |
| Grade | colunas iguais (até 4) com gap `space-6`; 2 colunas abaixo de 768px |
| Rótulo (`dt`) | Geist 600 13/20px, `fg`, com InfoHint quando o termo precisa de explicação |
| Valor (`dd`) | número em Geist Mono 500 24/28px `fg` e a unidade em Geist 400 15px `fg-muted`, separados por espaço: **1 850** kcal |
| Meta | Geist Mono 13/20px `fg-muted` embaixo do valor: "meta 2 157" |
| Nota | `body-sm` `fg-muted` embaixo da grade, com a fonte do dado: "Valores da TACO, 4ª edição." |

- O peso diferente entre número e unidade é o detalhe: o olho lê o número primeiro.
- O estado (acima ou abaixo da meta) vem em Badge ao lado da meta, nunca só pela cor do número.

### InfoHint

Explicação curta de um termo técnico (GET, fator atividade, % de adequação), ao lado do rótulo.

**Anatomia:** `button.ns-hint[aria-describedby]` com `Info` de 14px + `div.ns-hint__pop[role=tooltip]`.

| Parte | Especificação |
|---|---|
| Botão | 14px de ícone em `fg-muted`, área clicável de 24px, hover `fg` |
| Balão | largura máxima 240px, padding `space-2 space-3`, `body-sm` `fg`, fundo `surface-raised`, borda `line`, raio `radius-md`, `shadow-overlay` |

- Abre no hover e no foco, fecha no Esc. No toque, abre e fecha no clique.
- Uma ou duas frases. Se precisar de mais, é texto da página, não dica.

### PageToc

Índice das seções de uma página longa, à direita. É o feedback da sessão (avaliação do plano, adesão, pontos a melhorar).

**Anatomia:** `nav.ns-toc[aria-label="Nesta página"]` > `ol` > `li` > `a`.

| Parte | Especificação |
|---|---|
| Coluna | 200px, `position: sticky` no topo, a partir de 1280px; abaixo disso some |
| Trilho | borda esquerda 1px `line` |
| Item | padding `space-1 space-3`, Geist 500 13/20px, `fg-muted`, hover `fg` |
| Atual (`aria-current="true"`) | texto `fg` e barra de 2px em `fg` sobre o trilho (`margin-left: -1px`) |

- A barra do atual usa `fg`, não o lima: na sessão o Stepper já marca a etapa atual em lima, e dois sinais de "você está aqui" em lima competem.
- O item atual acompanha a rolagem com `IntersectionObserver`; sem JS, os links continuam levando à seção.

### Utilitários

| Classe | O que faz |
|---|---|
| `ns-num` | Geist Mono com `tabular-nums`, para qualquer número do motor |
| `ns-eyebrow` | estilo `eyebrow` (Geist Mono 500 12/16px, 0.04em, caixa alta, `fg-muted`), para título de seção e rótulo de dado |
| `ns-link` | link no texto: `fg`, Geist 500, sublinhado de 1px com `text-underline-offset: 3px`; hover tira o sublinhado. Sem cor de acento |
| `ns-icon` | 16 × 16px, sem preenchimento, traço `currentColor` de 1,5px com pontas arredondadas |
| `ns-sr` | esconde só da vista; o leitor de tela continua lendo (rótulos escondidos, "(concluída)") |
| `[hidden]` | `display: none !important`, para o atributo `hidden` vencer o `display` dos componentes |
| `:focus-visible` | anel global de 2px em `focus`, afastado 2px |

## Telas de referência

As telas ficam no canvas de telas (link no topo), em tamanho real. São a prova do sistema.

### Estrutura do app

Toda tela usa uma de duas estruturas. No canvas, a linha "Tela 1 · Estrutura do app".

- **Moldura:** a Sidebar e a Appbar formam um L em `chrome`. O conteúdo (`main.ns-main`) fica dentro dele em `bg`, com borda `line` em cima e à esquerda, raio `radius-lg` no canto superior esquerdo e o `glow` no fundo (`radial-gradient(600px circle at 0 0, var(--glow), transparent)`, sobre `bg`). No celular não há moldura: a Appbar fica em `chrome` com borda inferior `line` e o conteúdo ocupa a largura toda.
- **Página comum** (Início, Histórico, Nova sessão): Appbar e Sidebar expandida. O conteúdo tem largura máxima de 960px, centralizado na área que sobra, com padding `40px 40px space-16` e gap de 40px entre blocos.
- **Sessão** (etapas 2 a 5): Sidebar recolhida, Appbar com a trilha, o cabeçalho da sessão e, embaixo, o conteúdo da etapa (padding `space-8`), com o SidePanel ou a faixa dele à direita.
- **Cabeçalho da sessão** (`ns-session-head`): padding `28px space-8 space-6`, gap `space-6`, borda inferior `line`. Em cima, o Stepper. Embaixo, o título da etapa como `h2` (display 500 22/28px, "Plano alimentar"), a meta em Geist 14/20px `fg-muted` ("Diabetes tipo 2 · Dificuldade média") e, na ponta direita e centralizado com o título, o primário da etapa em `--sm`. O nome do paciente fica na trilha e o badge de IA fica na aba Conversa.
- **Etapa sem título (anamnese):** o cabeçalho é só o Stepper (`ns-session-head--steps`, padding `space-4 space-8`), e o primário fica na ponta direita da mesma linha. Se não couber, ele desce para a linha de baixo e continua à direita.
- **A ação principal é um verbo curto com o que vem depois, seguido de `ArrowRight`:** "Montar o plano" (anamnese), "Gerar cenários" (plano), "Ir para o retorno" (cenários). No desktop fica no cabeçalho da sessão, nunca na Appbar. No celular vai numa barra fixa embaixo (`ns-actionbar`: padding `space-3 space-4`, borda superior `line`, botão de largura total), exceto na anamnese, em que o composer ocupa o rodapé e a ação fica na faixa logo abaixo do Stepper.
- A dificuldade é texto na meta, não badge: as cores de estado ficam só para estado.
- **Início:** sem trilha. Título em dois tons ("Olá, Ana. Retome o João ou comece um paciente novo.") com o secundário "Nova sessão" ao lado, o card "Continuar de onde parou" (paciente, etapa com a barra de 5 segmentos e o primário "Continuar sessão") e a lista "Sessões recentes", em que a linha inteira é o link para o feedback (paciente, perfil, dificuldade, data em mono e "Ver feedback"), com o link "Ver histórico". Os títulos das seções são `eyebrow`. O estado vazio sai na tela 9.
- **Celular (360px):** Appbar com menu, logo, tema e conta. Na sessão vêm o Stepper compacto, o título da etapa (display 500 20/28px), a meta com o nome do paciente, os dois ícones do painel e a barra de ação embaixo.

### Configurar novo paciente (etapa 1)

- **No canvas:** página comum, com o Stepper no topo, o `h1` "Configurar novo paciente" e um parágrafo `fg-muted` que já diz que a IA cria o paciente. O formulário é um Card com o Select de patologia ou objetivo, o ChoiceCard de dificuldade, os badges neutros do que a ficha oculta contém e as ações "Gerar paciente e iniciar" (primário) e "Cancelar" (ghost). Sem badge "Gerado por IA" e sem Alert: a mensagem da IA aparecia quatro vezes.
- **No código:** a tela ainda segue a versão anterior, descrita abaixo, com a barra do topo antiga, até ser refeita.
- **Página:** largura máxima de 1040px, padding `space-8 space-6 space-12` e gap `space-8` entre blocos.
- **Cabeçalho (alinhado à esquerda):** eyebrow "ETAPA 1 DE 5 · CASO", `h1` com o badge "Gerado por IA" e um parágrafo `fg-muted` de até 62ch.
- **Formulário (Card):** ocupa a largura que sobra ao lado do "Como funciona", com Selects em grade de 2 colunas (Patologia ou objetivo, Dificuldade), um Alert `info` e as ações separadas por uma linha `line`: o primário "Gerar ficha oculta e iniciar consulta" e o ghost "Cancelar".
- **Como funciona:** a partir de 1024px, coluna lateral de 300px sem card, separada do formulário por uma borda esquerda `line`, com texto em `body-sm`; abaixo disso, Card embaixo do formulário. Contém "Como funciona a geração?", badges neutros com o que a ficha contém e a lista das 5 etapas. A etapa atual tem círculo de 24px em `fg`, com o número em `bg`, e `aria-current="step"`; as outras têm círculo com borda `line-strong`.
- **Mobile:** uma coluna com margem de 16px. Os cards perdem borda e fundo para não virar caixa dentro de caixa; o "Como funciona" fica separado por uma linha `line`.

### Anamnese (etapa 2)

- **Estrutura:** sessão, com o cabeçalho só de etapas e o primário "Montar o plano" na ponta direita. Antes de seguir, abre o Dialog "Encerrar a anamnese?".
- **Conversa:** coluna de até 720px. Abre com um card do paciente (avatar, "João, 45 anos", meta), o badge "Paciente simulado por IA", a queixa principal (`eyebrow` + texto) e a dica "Apresente-se e pergunte o motivo da consulta", que some quando a conversa começa. Embaixo vêm o log e o composer fixo no rodapé.
- **Painel:** SidePanel só com Anotações.
- **Sem cronômetro:** a consulta não tem limite de tempo no produto, então a tela não mostra relógio.
- **Celular:** Stepper compacto, a faixa com o botão de anotações e o primário, e o composer no rodapé.

### Consulta em andamento (versão anterior)

Substituída pela anamnese acima. Fica só como referência para a etapa 3: o plano deixou de ser aba da consulta e virou a etapa 3, com rota própria.

- **Topo:** logo, `h1` "Consulta em andamento" em display 18/26px, badge de dificuldade (`warning`) e o primário "Concluir e gerar simulação de adesão".
- **Corpo em duas colunas (1.1fr / 1fr), separadas por uma borda `line`:**
  - **Chat (esquerda):** cabeçalho com avatar, nome ("João, 45 anos"), meta em mono ("Diabetes tipo 2 · sedentário") e o badge "Paciente simulado por IA". Abaixo, o log com rolagem e padding `space-6` e o Composer fixo no rodapé.
  - **Ferramentas (direita):** Tabs (Anotações, Plano alimentar, Adesão) e o painel com dois blocos de número (eyebrow + `data-lg`: "GET · MIFFLIN-ST JEOR 2 157 kcal", "PLANO ATUAL / META 375 / 1 850"), os MealItems, o botão secundário "Adicionar refeição" e uma ajuda `body-sm`.
- **Mobile:** uma coluna, com Chat como primeira aba.

## Tokens no Tailwind 4

Para o `frontend/src/app/globals.css`. O `next-themes` está com `attribute="class"`. Como o escuro é a base, os valores dele ficam no `:root` e o claro sobrescreve com `.light`. O `ThemeProvider` do `layout.tsx` usa `defaultTheme="system"` para acompanhar o sistema operacional.

O bloco `@theme inline` expõe esses valores ao Tailwind, e o mesmo arquivo define o anel de foco global (`:focus-visible`) e o texto base do `body` (15/24).


Com isso, as classes saem com os nomes dos tokens: `bg-bg`, `bg-surface`, `bg-surface-raised`, `bg-surface-hover`, `bg-chrome`, `border-line`, `border-line-strong`, `text-fg`, `text-fg-secondary`, `text-fg-muted`, `bg-accent`, `text-on-accent`, `bg-success-soft`, `text-danger`, `outline-focus`, `font-display`, `font-mono`, `rounded-md`, `rounded-lg`, `rounded-xl`, `rounded-pill` e `shadow-overlay`. O espaçamento já é a escala padrão do Tailwind (`p-4` = 16px, `gap-6` = 24px). Não é preciso redefinir.

As fontes entram pelo `next/font/google` no `layout.tsx`: `Geist` (`--font-geist-sans`, que também é o `display`) e `Geist_Mono` (`--font-geist-mono`).
