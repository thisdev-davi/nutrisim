# content

Material didático que o NutriSim usa para avaliar as consultas: **rubricas** de avaliação e **roteiros** de anamnese. Tudo em Markdown, para que professores do curso de Nutrição revisem e editem sem conhecimento técnico.

**Responsáveis:** Arthur Pomarolli (organização), com revisão do professor de Nutrição.

## Estrutura prevista

```text
content/
├── rubricas/     critérios de correção da consulta, por perfil     NS-049
└── roteiros/     o que uma boa anamnese deve investigar, por perfil NS-049
```

## Formato dos arquivos

Cada arquivo começa com um cabeçalho de metadados (front matter). O sistema usa esse cabeçalho para escolher quais trechos carregar em cada caso:

```markdown
---
tipo: rubrica            # rubrica | roteiro
perfis: [adulto-hipertensao, adulto-diabetes]
versao: 1
revisado_por: Nome do(a) professor(a)
revisado_em: 2026-11-10
---

# Rubrica: adulto com hipertensão

## Investigação do consumo de sódio
...
```

## Como o sistema usa este material

A avaliação por rubrica (NS-051) carrega as seções cujo `perfis` inclui o perfil do caso e as envia ao prompt de correção. É uma recuperação por **filtro de metadados**, sem banco vetorial, porque o volume de material é pequeno (ver ADR-004 em [`docs/decisoes.md`](../docs/decisoes.md)).

## Como um professor edita

1. Abrir o arquivo no GitHub e clicar no ícone de lápis (*Edit this file*).
2. Alterar o texto e atualizar `versao`, `revisado_por` e `revisado_em`.
3. Salvar em *Commit changes* e escolher "Create a new branch and start a pull request".

A equipe revisa o PR e integra a mudança.
