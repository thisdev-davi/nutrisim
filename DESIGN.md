# Design do NutriSim

Identidade visual e componentes da interface do NutriSim. Este arquivo é a referência para o código: quando ele e a vitrine divergirem, vale o que está aqui.

- **Vitrine visual (design system):** https://claude.ai/artifact/LyyG6Us3oibo3ad5YrhfZb. Lá estão os previews ao vivo de cada componente, as telas de prova e as logos em SVG.
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

A interface tem que passar rigor clínico com cara de ferramenta moderna: escura, precisa e sem enfeite. A referência de linguagem é o site do Neon, com fundo quase preto, bordas finas, tipografia com tracking negativo, mono nos dados e um único acento usado com parcimônia. O grid decorativo e as animações de vitrine ficaram de fora porque não cabem num app clínico.

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

O tema **escuro é o padrão** e vem primeiro. O claro usa os mesmos nomes de token. Os neutros são zinc (frios).

O lima (`accent`) é o recurso mais escasso do sistema. Ele só aparece na ação principal da tela, no anel de foco e no badge de IA. Navegação ativa, aba ativa e etapa atual usam `fg`, nunca o lima. Os estados têm paleta própria e nunca usam o lima. Todo estado vem com ícone e texto, nunca só com cor.

### Neutros

| Token | Escuro | Claro | Uso |
|---|---|---|---|
| `bg` | `#09090b` | `#fafafa` | Fundo da página |
| `surface` | `#18181b` | `#ffffff` | Cards, painéis, campos de formulário, balão do paciente |
| `surface-raised` | `#27272a` | `#f4f4f5` | Balão do estudante, hover de botão fantasma, trilho da barra de adesão |
| `line` | `#27272a` | `#e4e4e7` | Bordas de 1px entre áreas e em cards. Separa sem sombra. É decorativa e não marca controles |
| `line-strong` | `#71717a` | `#8a8a93` | Borda de controles (input, select, botão secundário). Contraste de 3:1 sobre `bg`, `surface` e `surface-raised` |
| `fg` | `#fafafa` | `#09090b` | Texto principal sobre `bg`, `surface` e `surface-raised` |
| `fg-muted` | `#a1a1aa` | `#52525b` | Texto secundário, metadados, placeholders. 4.5:1 sobre `bg`, `surface` e `surface-raised` |

### Acento (lima)

| Token | Escuro | Claro | Uso |
|---|---|---|---|
| `accent` | `#a3e635` | `#4d7c0f` | Ação principal, foco, badge de IA. Como texto, só sobre `bg`, `surface` ou `accent-soft` |
| `accent-hover` | `#bef264` | `#3f6212` | Hover do botão primário |
| `accent-soft` | `#1a2e05` | `#ecfccb` | Fundo tingido atrás de texto `accent` |
| `on-accent` | `#09090b` | `#ffffff` | Texto e ícone sobre preenchimento `accent` |
| `focus` | = `accent` | = `accent` | Anel de foco do teclado |

O lima brilha no escuro. No claro ele escurece para `#4d7c0f` para manter o contraste. Nunca use o lima claro (`#a3e635`) sobre fundo claro.

### Estados

| Token | Escuro | Claro | Uso |
|---|---|---|---|
| `success` | `#34d399` | `#047857` | Estado bom (adesão alta, meta atingida). É esmeralda, nunca o lima |
| `success-soft` | `#022c22` | `#d1fae5` | Fundo de badge e alerta de sucesso |
| `warning` | `#fbbf24` | `#92400e` | Atenção (adesão moderada, restrição perto do limite) |
| `warning-soft` | `#451a03` | `#fef3c7` | Fundo de badge e alerta de atenção |
| `danger` | `#f87171` | `#b91c1c` | Erro e estado crítico (adesão baixa, restrição violada) |
| `danger-soft` | `#450a0a` | `#fee2e2` | Fundo de badge e alerta de erro |

O texto de estado vai sobre `bg`, `surface` ou o `-soft` correspondente.

## Tipografia

O sistema usa três famílias, cada uma com um papel. Todas vêm do Google Fonts (no Next, via `next/font/google`).

| Família | Token | Papel | Pesos |
|---|---|---|---|
| **Space Grotesk** | `display` | Só logotipo, `h1`, `h2` e o título da landing | 500, 600, 700 |
| **Geist** | `sans` | Toda a interface e o texto corrido | 400, 500, 600 |
| **Geist Mono** | `mono` | Dados do motor, horários, metadados e rótulos técnicos | 400, 500 |

Pilhas de fallback:

```css
--font-display: "Space Grotesk", "Geist", system-ui, sans-serif;
--font-sans: "Geist", system-ui, sans-serif;
--font-mono: "Geist Mono", ui-monospace, "SFMono-Regular", monospace;
```

### Escala

| Estilo | Família | Tamanho / altura de linha | Peso | Tracking | Uso |
|---|---|---|---|---|---|
| `display-xl` | display | 56 / 60px | 700 | -0.03em | Título da landing, uma vez por página |
| `h1` | display | 32 / 38px | 600 | -0.02em | Título da página |
| `h2` | display | 24 / 30px | 600 | -0.015em | Título de seção |
| `h3` | sans | 18 / 26px | 600 | 0 | Título de card e de grupo |
| `body` | sans | 15 / 24px | 400 | 0 | Texto corrido e mensagens do chat |
| `body-sm` | sans | 13 / 20px | 400 | 0 | Ajuda de campo, legenda |
| `control` | sans | 14 / 20px | 500 | 0 | Botão padrão e aba |
| `label` | sans | 13 / 16px | 500 | 0 | Rótulo de campo e botão pequeno |
| `data-lg` | mono | 24 / 28px | 500 | 0 | Número de destaque do motor (GET, total do plano) |
| `data` | mono | 14 / 20px | 400 | 0 | Quantidades, nutrientes e porcentagens em linhas e tabelas |
| `eyebrow` | mono | 12 / 16px | 500 | 0.04em | Rótulo técnico curto acima de título ou valor (fonte do dado, horário), em caixa alta |

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

| Token | Valor | Uso |
|---|---|---|
| `radius-md` | 8px | Botões, inputs, selects, itens pequenos |
| `radius-lg` | 12px | Cards, painéis, balões de chat |
| `radius-pill` | 9999px | Só badges, chips e avatares |

### Borda, não sombra

As áreas se separam pela borda `line` (1px) e pelo contraste de `surface` sobre `bg`. Os controles usam `line-strong`. A única sombra do sistema é a de camadas flutuantes:

| Token | Escuro | Claro | Uso |
|---|---|---|---|
| `shadow-overlay` | `0 8px 24px rgba(0,0,0,.5)` | `0 8px 24px rgba(9,9,11,.12)` | Menus, popovers e diálogos. Nunca em cards |

## Movimento

O movimento se limita ao necessário: transições de 150ms em hover (cor de fundo, borda e texto) e o cursor piscando no streaming do chat. Tudo para com `prefers-reduced-motion: reduce`.

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
| Enviar | `Send` | Composer do chat |
| Lápis | `Pencil` | Editar refeição |
| Mais | `Plus` | Adicionar refeição |
| Info | `Info` | Dica em formulário |
| Check, triângulo, círculo | `Check`, `TriangleAlert`, `CircleAlert` | Badges de sucesso, atenção e erro |

## Logo

O símbolo é um balão de fala com uma folha em lima. A folha é um furo real, então o fundo aparece através dela. O logotipo "**Nutri**Sim" é Space Grotesk (Nutri 700, Sim 400), já convertido em path.

| Arquivo | Quando usar |
|---|---|
| `nutrisim-escuro.svg` | Fundo escuro (símbolo `#A3E635`, texto `#F5F5F4`). É a versão padrão |
| `nutrisim-claro.svg` | Fundo claro (símbolo `#4D7C0F`, texto `#0C0A09`) |
| `nutrisim-mono-preto.svg` / `nutrisim-mono-branco.svg` | Uma cor só, para impressão e fundos coloridos |
| `nutrisim-simbolo-escuro.svg` / `nutrisim-simbolo-claro.svg` | Só o símbolo, para avatar e espaços quadrados |

- **Área de respiro:** a altura do rabicho do balão, em volta da logo.
- **Altura mínima:** 24px para a logo completa e 16px para o símbolo. Na barra do app ela tem 28px.
- O favicon (`app/icon.svg`) troca de cor sozinho com o tema.
- Não recolorir, não trocar a fonte e não aplicar o lima sobre fundo claro.

Os SVGs estão na vitrine, no grupo Logos.

## Acessibilidade

- O texto tem contraste de 4.5:1 sobre o fundo em que é usado, nos dois temas. Bordas de controle, foco e ícones têm 3:1.
- Alvo de toque mínimo de 44px (botão padrão, aba, campo).
- Foco visível em tudo: anel de 2px em `focus`, afastado 2px do elemento. Nos campos o afastamento é 0 e a borda some.
- Chat como `role="log"`, abas no padrão tablist e barra de adesão como `role="meter"`.
- Estado nunca é só cor: sempre ícone e texto.
- Todo campo tem `<label>` visível. Quando o rótulo não pode aparecer (composer do chat), ele fica escondido só visualmente, mas continua no HTML.

## Componentes

Todos os componentes são HTML e CSS com classes `ns-*`, sem JS próprio. Os valores de cada um usam os tokens acima. No app eles viram componentes React em `components/ui/`.

### Button

Botão de ação. `primary` é para a única ação principal da tela, `secondary` para as demais e `ghost` para ações de baixo peso.

**Anatomia:** `button.ns-btn` (ou `a.ns-btn`) com ícone opcional à esquerda e rótulo.

| Variante | Fundo | Texto | Borda | Hover |
|---|---|---|---|---|
| `--primary` | `accent` | `on-accent` | transparente | fundo `accent-hover` |
| `--secondary` | transparente | `fg` | `line-strong` | fundo `surface-raised` |
| `--ghost` | transparente | `fg-muted` | transparente | fundo `surface-raised`, texto `fg` |

| Tamanho | Altura | Padding horizontal | Fonte |
|---|---|---|---|
| padrão | 44px | `space-4` (16px) | Geist 500, 14px |
| `--sm` | 36px | `space-3` (12px) | Geist 500, 13px |
| `--icon` | 44 × 44px | 0 | (só ícone) |

- **Geral:** raio `radius-md`, gap de `space-2` entre ícone (16px) e rótulo, `white-space: nowrap` e transição de 150ms.
- **Disabled:** opacidade .45 e `cursor: not-allowed`.
- **Um primário por tela.** Se dois botões pedem lima, um deles é secundário.
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
| Caixa | altura 44px, padding horizontal `space-3`, borda 1px `line-strong`, raio `radius-md`, fundo `surface`, texto `fg` em `body` (15/24px) |
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
- Valores numéricos (peso, gramas, kcal) usam `ns-num` (Geist Mono, tabular) e o `inputmode` adequado.
- No erro, coloque `aria-invalid="true"` e um `aria-describedby` que aponte para o `ns-error`. A mensagem diz como corrigir.

### Select

Lista de opções sobre o `<select>` nativo, com a mesma caixa do Input e um chevron desenhado por cima.

**Anatomia:** `div.ns-select-wrap` (relativo) > `select.ns-select` + `svg.ns-icon` (chevron).

- **Caixa:** igual ao Input, com `appearance: none`, `padding-right: 40px` e `cursor: pointer`.
- **Chevron:** 16px, cor `fg-muted`, posição absoluta (`right: space-3`, `top: 14px`) e `pointer-events: none`.
- **Hover e foco:** iguais ao Input.
- É nativo de propósito: teclado, leitor de tela e o seletor do celular vêm de graça. Só troque por um menu próprio se precisar de busca (ex.: alimentos da TACO).
- Os filtros do histórico (Patologia, Dificuldade, Data) usam este mesmo componente.

### Tabs

Abas das ferramentas clínicas da consulta (Chat, Anotações, Plano alimentar, Adesão), com o padrão ARIA de tablist e navegação pelas setas.

**Anatomia:** `div.ns-tabs[role=tablist]` > `button.ns-tab[role=tab]`. Os painéis (`role="tabpanel"`) ficam com o consumidor, ligados à aba por `aria-controls`.

| Parte | Especificação |
|---|---|
| Lista | flex com gap `space-1`, borda inferior 1px `line`, rolagem horizontal |
| Aba | altura 44px, padding `0 space-4`, Geist 500 14px, cor `fg-muted`, sublinhado de 2px transparente sobreposto à borda (`margin-bottom: -1px`) |
| hover | texto `fg` |
| ativa (`aria-selected="true"`) | texto `fg` e sublinhado de 2px em `fg` |

- A aba ativa usa `fg`, não lima: o lima fica para a ação principal.
- Aba inativa recebe `tabindex="-1"`, e as setas movem o foco.
- No mobile, Chat é uma aba. No desktop o chat fica fixo à esquerda e as abas mostram só as ferramentas.
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

Mensagens da anamnese. O paciente simulado fica à esquerda e o estudante à direita. Durante o streaming aparece um cursor.

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
├── input.ns-input
└── button.ns-btn--secondary.ns-btn--icon (Enviar)
```

| Parte | Especificação |
|---|---|
| Chat | coluna com gap `space-4` |
| Mensagem | largura máxima de 80% da coluna, gap `space-3` entre avatar e corpo |
| Avatar | 32px, raio `radius-pill`, borda `line-strong`, fundo `surface`, iniciais em Geist Mono 500 12px `fg-muted` |
| Balão | padding `10px 14px`, raio `radius-lg`, `body` (15/24px), quebra de palavra longa |
| Balão do paciente | fundo `surface`, borda `line`, canto inferior esquerdo com raio de 4px |
| Balão do estudante | fundo `surface-raised`, sem borda, canto inferior direito com raio de 4px |
| Meta | Geist Mono 12/16px, `fg-muted` (hora; "João · 09:12") |
| Cursor | 8 × 18px em `fg`, pisca a cada 1s (`steps(1)`) |
| Composer | flex com gap `space-2`, padding `space-3`, borda superior 1px `line`, input ocupa o resto |

- Os balões não têm lima. A conversa é neutra e o acento fica para a ação principal.
- Durante o streaming, o balão tem `ns-cursor` no fim do texto e `aria-busy="true"`, e a meta diz "João está respondendo…". Com `prefers-reduced-motion`, o cursor para de piscar.
- O contêiner é `role="log"` para o leitor de tela anunciar as mensagens novas.
- O botão Enviar é secundário só de ícone. O primário da tela de consulta é "Concluir…".

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
- `--info` é a dica de formulário. Não use alerta para conteúdo que cabe num `ns-help`.

### Utilitários

| Classe | O que faz |
|---|---|
| `ns-num` | Geist Mono com `tabular-nums`, para qualquer número do motor |
| `ns-eyebrow` | estilo `eyebrow` (Geist Mono 500 12/16px, tracking 0.04em, caixa alta, `fg-muted`) |
| `ns-icon` | 16 × 16px, sem preenchimento, traço `currentColor` de 1,5px com pontas arredondadas |
| `:focus-visible` | anel global de 2px em `focus`, afastado 2px |

## Telas de referência

As duas telas da vitrine mostram os componentes juntos. São a prova do sistema, em desktop.

### Configurar novo paciente (etapa 1)

- **Barra do app:** logo de 28px, links de navegação (Início, Casos, Histórico) como botões ghost de 36px com `aria-current="page"` em `surface-raised`, e Perfil com avatar de 24px. Borda inferior `line`.
- **Página:** largura máxima de 1040px, padding `space-8 space-6 space-12` e gap `space-8` entre blocos.
- **Cabeçalho:** "Voltar" (ghost sm), eyebrow "ETAPA 1 DE 5 · CASO", `h1` com o badge "Gerado por IA" e um parágrafo `fg-muted` de até 62ch.
- **Grade de duas colunas (1.35fr / 1fr):**
  - **Formulário (Card):** quatro Selects em grade 2 × 2 (Patologia ou objetivo, Dificuldade, Faixa etária, Sexo), um Alert `info`, e as ações separadas por uma linha `line`: o primário "Gerar ficha oculta e iniciar consulta" e o ghost "Cancelar".
  - **Lateral (Card):** "Como funciona a geração?", badges neutros com o que a ficha contém e a lista das 5 etapas. A etapa atual tem círculo de 24px em `fg`, com o número em `bg`, e `aria-current="step"`; as outras têm círculo com borda `line-strong`.

### Consulta em andamento (etapa 2, aba Plano ativa)

- **Topo:** logo, `h1` "Consulta em andamento" em display 18/26px, badge de dificuldade (`warning`), cronômetro em mono e o primário "Concluir e gerar simulação de adesão".
- **Corpo em duas colunas (1.1fr / 1fr), separadas por uma borda `line`:**
  - **Chat (esquerda):** cabeçalho com avatar, nome ("João, 45 anos"), meta em mono ("Diabetes tipo 2 · sedentário") e o badge "Paciente simulado por IA". Abaixo, o log com rolagem e padding `space-6` e o Composer fixo no rodapé.
  - **Ferramentas (direita):** Tabs (Anotações, Plano alimentar, Adesão) e o painel com dois blocos de número (eyebrow + `data-lg`: "GET · MIFFLIN-ST JEOR 2 157 kcal", "PLANO ATUAL / META 375 / 1 850"), os MealItems, o botão secundário "Adicionar refeição" e uma ajuda `body-sm`.
- **Mobile:** uma coluna, com Chat como primeira aba.

## Tokens no Tailwind 4

Para o `frontend/src/app/globals.css`. O `next-themes` está com `attribute="class"`. Como o escuro é o padrão, os valores dele ficam no `:root` e o claro sobrescreve com `.light`. Por isso o `ThemeProvider` do `layout.tsx` usa `defaultTheme="dark"`.

```css
@import "tailwindcss";

:root {
  --bg: #09090b;
  --surface: #18181b;
  --surface-raised: #27272a;
  --line: #27272a;
  --line-strong: #71717a;
  --fg: #fafafa;
  --fg-muted: #a1a1aa;
  --accent: #a3e635;
  --accent-hover: #bef264;
  --accent-soft: #1a2e05;
  --on-accent: #09090b;
  --success: #34d399;
  --success-soft: #022c22;
  --warning: #fbbf24;
  --warning-soft: #451a03;
  --danger: #f87171;
  --danger-soft: #450a0a;
  --overlay: 0 8px 24px rgba(0, 0, 0, 0.5);
}

.light {
  --bg: #fafafa;
  --surface: #ffffff;
  --surface-raised: #f4f4f5;
  --line: #e4e4e7;
  --line-strong: #8a8a93;
  --fg: #09090b;
  --fg-muted: #52525b;
  --accent: #4d7c0f;
  --accent-hover: #3f6212;
  --accent-soft: #ecfccb;
  --on-accent: #ffffff;
  --success: #047857;
  --success-soft: #d1fae5;
  --warning: #92400e;
  --warning-soft: #fef3c7;
  --danger: #b91c1c;
  --danger-soft: #fee2e2;
  --overlay: 0 8px 24px rgba(9, 9, 11, 0.12);
}

@theme inline {
  --color-bg: var(--bg);
  --color-surface: var(--surface);
  --color-surface-raised: var(--surface-raised);
  --color-line: var(--line);
  --color-line-strong: var(--line-strong);
  --color-fg: var(--fg);
  --color-fg-muted: var(--fg-muted);
  --color-accent: var(--accent);
  --color-accent-hover: var(--accent-hover);
  --color-accent-soft: var(--accent-soft);
  --color-on-accent: var(--on-accent);
  --color-focus: var(--accent);
  --color-success: var(--success);
  --color-success-soft: var(--success-soft);
  --color-warning: var(--warning);
  --color-warning-soft: var(--warning-soft);
  --color-danger: var(--danger);
  --color-danger-soft: var(--danger-soft);

  --font-sans: var(--font-geist-sans), system-ui, sans-serif;
  --font-mono: var(--font-geist-mono), ui-monospace, "SFMono-Regular", monospace;
  --font-display: var(--font-space-grotesk), var(--font-geist-sans), system-ui, sans-serif;

  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-pill: 9999px;

  --shadow-overlay: var(--overlay);
}

@layer base {
  :focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }
}

body {
  background: var(--bg);
  color: var(--fg);
  font-size: 15px;
  line-height: 24px;
}
```

Com isso, as classes saem com os nomes dos tokens: `bg-bg`, `bg-surface`, `bg-surface-raised`, `border-line`, `border-line-strong`, `text-fg`, `text-fg-muted`, `bg-accent`, `text-on-accent`, `bg-success-soft`, `text-danger`, `outline-focus`, `font-display`, `font-mono`, `rounded-md`, `rounded-lg`, `rounded-pill` e `shadow-overlay`. O espaçamento já é a escala padrão do Tailwind (`p-4` = 16px, `gap-6` = 24px). Não é preciso redefinir.

As fontes entram pelo `next/font/google` no `layout.tsx`: `Geist` (`--font-geist-sans`), `Geist_Mono` (`--font-geist-mono`) e `Space_Grotesk` (`--font-space-grotesk`).
