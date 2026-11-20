# regras de coerencia entre o perfil e o cenario realista (NS-047)
# deterministicas, sem llm nem banco: o runner mede a taxa com --cenarios
import re
from collections.abc import Mapping

from app.api.alimentos import normalizar_busca
from app.motor import restricoes
from app.schemas.api import CenarioRealista, NovoPlano
from app.schemas.ficha import Ficha

# adesao a partir da qual a refeicao conta como seguida quase sempre
ADESAO_ALTA = 0.8
# horas (inclusive) em que cada refeicao cai, pela palavra do nome
JANELAS = {
    "cafe": (4, 10),
    "desjejum": (4, 10),
    "almoco": (11, 14),
    # ate 19h: a fruta antes da academia ou da aula da noite ainda e lanche
    "lanche": (14, 19),
    "jantar": (18, 22),
    "ceia": (21, 24),
}

# plano simples e igual para todas as fichas, so com ids que tem preco; a ceia
# fica de proposito: quase nenhum recordatorio tem refeicao depois das 21h
PLANO_FIXO = NovoPlano.model_validate({
    "refeicoes": [
        {
            "nome": "Café da manhã",
            "itens": [
                {"alimento_id": 53, "gramas": 50},  # pao frances
                {"alimento_id": 458, "gramas": 200},  # leite integral
                {"alimento_id": 511, "gramas": 10},  # cafe em po
            ],
        },
        {
            "nome": "Almoço",
            "itens": [
                {"alimento_id": 4, "gramas": 80},  # arroz
                {"alimento_id": 562, "gramas": 60},  # feijao carioca
                {"alimento_id": 402, "gramas": 120},  # frango
                {"alimento_id": 157, "gramas": 60},  # tomate
            ],
        },
        {
            "nome": "Lanche da tarde",
            "itens": [{"alimento_id": 182, "gramas": 100}],  # banana prata
        },
        {
            "nome": "Jantar",
            "itens": [
                {"alimento_id": 4, "gramas": 60},
                {"alimento_id": 562, "gramas": 50},
                {"alimento_id": 489, "gramas": 50},  # ovo
                {"alimento_id": 115, "gramas": 50},  # couve
            ],
        },
        {"nome": "Ceia", "itens": [{"alimento_id": 458, "gramas": 150}]},
    ]
})


def substituto_com_aversao(ficha: Ficha, cenario: CenarioRealista) -> list[str]:
    """troca para um alimento que o paciente diz nao comer.

    So as aversoes: alimento evitado pelo caso (torresmo, doce) e o que o
    paciente costuma comer, entao trocar por ele e realista, nao incoerente.
    Casa palavra no nome da TACO como o motor (restricoes._evitados).

    Returns:
        uma mensagem por troca incoerente.
    """
    termos = {
        a: [
            p.removesuffix("s")
            for p in normalizar_busca(a).split()
            if len(p) >= restricoes.LETRAS_MINIMAS
        ]
        for a in ficha.paciente.aversoes
    }
    return [
        f"{s.refeicao}: {s.substituto} no lugar de {s.original}, mas tem aversao "
        f"a {aversao}"
        for s in cenario.substituicoes
        for aversao, palavras in termos.items()
        if any(p in normalizar_busca(s.substituto) for p in palavras)
    ]


def troca_estoura_orcamento(
    ficha: Ficha,
    plano: NovoPlano,
    cenario: CenarioRealista,
    precos: Mapping[int, float],
) -> list[str]:
    """trocas que encarecem o dia e o deixam acima do orcamento.

    Returns:
        uma mensagem, ou vazia.
    """
    # ponytail: porcao inteira e mesmas gramas do original, como no cenario;
    # sem preco conta zero no plano e tira a troca da conta. usar a adesao se o
    # custo passar a ser o do realista
    gramas = {
        (r.nome, i.alimento_id): i.gramas for r in plano.refeicoes for i in r.itens
    }
    custo = sum(
        precos.get(i.alimento_id, 0) * i.gramas / 100
        for r in plano.refeicoes
        for i in r.itens
    )
    extra = sum(
        (precos.get(s.substituto_id, 0) - precos.get(s.original_id, 0))
        * gramas[s.refeicao, s.original_id]
        / 100
        for s in cenario.substituicoes
        if s.substituto_id in precos and s.original_id in precos
    )
    orcamento = ficha.paciente.orcamento_mensal_reais / 30
    if extra > 0 and custo + extra > orcamento:
        return [
            f"trocas sobem o dia para R$ {custo + extra:.2f}, acima do "
            f"orcamento de R$ {orcamento:.2f}"
        ]
    return []


def adesao_fora_da_rotina(ficha: Ficha, cenario: CenarioRealista) -> list[str]:
    """adesao alta numa refeicao que o dia tipico do paciente nao tem.

    Returns:
        uma mensagem por refeicao incoerente.
    """
    # ponytail: janela fixa pelo nome e hora "Nh" do recordatorio; nome livre
    # ("refeicao 3") e turno da noite escapam. usar a hora do plano se ele tiver
    horas = [
        int(h)
        for linha in ficha.paciente.recordatorio
        for h in re.findall(r"(\d{1,2})h", linha)
    ]
    mensagens = []
    for a in cenario.adesao:
        nome = normalizar_busca(a.refeicao)
        janela = next((j for p, j in JANELAS.items() if p in nome), None)
        if janela is None or a.adesao < ADESAO_ALTA:
            continue
        if not any(janela[0] <= h <= janela[1] for h in horas):
            mensagens.append(
                f"{a.refeicao}: adesao {a.adesao:g}, mas o recordatorio nao "
                f"tem refeicao entre {janela[0]}h e {janela[1]}h"
            )
    return mensagens


def violacoes(
    ficha: Ficha,
    plano: NovoPlano,
    cenario: CenarioRealista,
    precos: Mapping[int, float],
) -> dict[str, list[str]]:
    """todas as regras de coerencia de um cenario.

    Returns:
        regra -> mensagens; so as regras violadas.
    """
    por_regra = {
        "substituto_com_aversao": substituto_com_aversao(ficha, cenario),
        "troca_estoura_orcamento": troca_estoura_orcamento(
            ficha, plano, cenario, precos
        ),
        "adesao_fora_da_rotina": adesao_fora_da_rotina(ficha, cenario),
    }
    return {regra: m for regra, m in por_regra.items() if m}
