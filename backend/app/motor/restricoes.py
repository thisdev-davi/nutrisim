# restricoes do caso conferidas no plano (NS-044): funcao pura, sem ia
#
# os limites vem da ficha (app/api/caso.py RESTRICOES), com as fontes de
# content/perfis.md:
#   sodio <= 2000 mg/dia: OMS (2012); Diretrizes Brasileiras de Hipertensao
#     Arterial (2020)
#   fibras >= 14 g/1000 kcal: Sociedade Brasileira de Diabetes (2023)
#   gordura saturada < 10% do VET: OMS (2023)
#   proteina 1,2 a 1,5 g/kg/dia: PROT-AGE (Bauer et al., 2013)
#   alimentos evitados (doces, bebidas adocadas): OMS, acucares (2015)
# VET = kcal total do plano; orcamento diario = mensal / 30
from app.api.alimentos import normalizar_busca
from app.schemas.api import Plano, Violacao
from app.schemas.ficha import Ficha

# palavras menores ("de", "com", "pao") casariam com quase todo nome da TACO
LETRAS_MINIMAS = 4


def verificar_restricoes(ficha: Ficha, plano: Plano) -> list[Violacao]:
    """confere o plano calculado contra as restricoes e o orcamento da ficha.

    Args:
        ficha: ficha oculta do caso.
        plano: plano ja calculado pelo motor.

    Returns:
        violacoes encontradas; vazia quando o plano cumpre tudo.
    """
    r = ficha.restricoes
    total = plano.total.valores
    kcal = total["kcal"]
    peso = ficha.paciente.peso_kg
    violacoes = []

    if r.sodio_max_mg is not None and total["sodio"] > r.sodio_max_mg:
        violacoes.append(
            Violacao(
                tipo="sodio",
                mensagem=f"sodio de {total['sodio']:.0f} mg passa do limite "
                f"de {r.sodio_max_mg:.0f} mg/dia",
                refeicao=_maior(plano, "sodio"),
            )
        )

    # sem kcal nao ha razao por VET; o plano vazio ja aparece na adequacao
    if r.fibras_min_g_por_1000kcal is not None and kcal > 0:
        fibras = total["fibra_alimentar"] / kcal * 1000
        if fibras < r.fibras_min_g_por_1000kcal:
            violacoes.append(
                Violacao(
                    tipo="fibras",
                    mensagem=f"fibras de {fibras:.1f} g/1000 kcal abaixo do "
                    f"minimo de {r.fibras_min_g_por_1000kcal:g}",
                )
            )

    if r.gordura_saturada_max_pct_vet is not None and kcal > 0:
        pct = total["gordura_saturada"] * 9 / kcal * 100
        if pct >= r.gordura_saturada_max_pct_vet:
            violacoes.append(
                Violacao(
                    tipo="gordura_saturada",
                    mensagem=f"gordura saturada em {pct:.1f}% do VET, o limite "
                    f"e menos de {r.gordura_saturada_max_pct_vet:g}%",
                    refeicao=_maior(plano, "gordura_saturada"),
                )
            )

    g_kg = total["proteina"] / peso
    if r.proteina_g_kg_min is not None and g_kg < r.proteina_g_kg_min:
        violacoes.append(
            Violacao(
                tipo="proteina",
                mensagem=f"proteina de {g_kg:.2f} g/kg abaixo do minimo "
                f"de {r.proteina_g_kg_min:g} g/kg",
            )
        )
    if r.proteina_g_kg_max is not None and g_kg > r.proteina_g_kg_max:
        violacoes.append(
            Violacao(
                tipo="proteina",
                mensagem=f"proteina de {g_kg:.2f} g/kg acima do maximo "
                f"de {r.proteina_g_kg_max:g} g/kg",
                refeicao=_maior(plano, "proteina"),
            )
        )

    violacoes += _evitados(r.alimentos_evitados, plano)

    orcamento = ficha.paciente.orcamento_mensal_reais / 30
    if plano.custo_diario_reais > orcamento:
        violacoes.append(
            Violacao(
                tipo="orcamento",
                mensagem=f"custo de R$ {plano.custo_diario_reais:.2f}/dia passa "
                f"do orcamento de R$ {orcamento:.2f}/dia",
            )
        )
    return violacoes


def _maior(plano: Plano, nutriente: str) -> str:
    """refeicao que mais contribui: e onde o estudante deve mexer primeiro.

    Returns:
        nome da refeicao.
    """
    return max(
        plano.refeicoes, key=lambda r: r.composicao.valores.get(nutriente, 0)
    ).nome


def _evitados(evitados: list[str], plano: Plano) -> list[Violacao]:
    """itens cujo nome da TACO tem alguma palavra do alimento evitado.

    Compara sem acento e sem o plural ("bebidas adocadas" vira "bebida" e
    "adocada"); palavras com menos de LETRAS_MINIMAS letras ficam de fora.

    Returns:
        uma violacao por item evitado, com a refeicao e o alimento_id.
    """
    # ponytail: casa palavra no nome da TACO; "refrigerante" ou "suco" nao casam
    # com "bebidas adocadas" e "bebida lactea" casa. lista de ids por perfil se precisar
    termos = {
        e: [
            p.removesuffix("s")
            for p in normalizar_busca(e).split()
            if len(p) >= LETRAS_MINIMAS
        ]
        for e in evitados
    }
    violacoes = []
    for refeicao in plano.refeicoes:
        for item in refeicao.itens:
            nome = normalizar_busca(item.nome)
            for evitado, palavras in termos.items():
                if any(p in nome for p in palavras):
                    violacoes.append(
                        Violacao(
                            tipo="alimento_evitado",
                            mensagem=f"{item.nome} entra em {evitado}, que o caso "
                            "pede para evitar",
                            refeicao=refeicao.nome,
                            alimento_id=item.alimento_id,
                        )
                    )
                    break
    return violacoes
