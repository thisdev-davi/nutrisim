# projecao de peso (NS-045): funcao pura, sem ia
#
# fontes:
# HALL, K. D. et al. Quantification of the effect of energy imbalance on
# bodyweight. The Lancet, v. 378, n. 9793, p. 826-837, 2011.
# HALL, K. D. What is the required energy deficit per unit weight loss?
# International Journal of Obesity, v. 32, n. 3, p. 573-576, 2008.
#
# versao simplificada do modelo dinamico de Hall: a cada semana o peso muda
# 7 x (kcal_dia - get(peso)) / RHO, com o get recalculado pelo peso da semana.
# por isso o deficit encolhe a medida que o peso cai, ao contrario da regra fixa
# de 7700 kcal/kg. RHO e a densidade energetica do tecido perdido ou ganho, com
# 75% de gordura (9440 kcal/kg) e 25% de massa magra (1816 kcal/kg).
# ponytail: particao fixa e sem termogenese adaptativa; vale para poucas semanas.
# para meses, trocar pelo modelo completo (particao de Forbes, massa gorda).
from app.motor import energia
from app.motor.energia import Atividade, Sexo

RHO_KCAL_KG = 0.75 * 9440 + 0.25 * 1816

# faixas plausiveis; os limites sao aceitos
FAIXAS = {"kcal_dia": (0, 10000), "semanas": (1, 12)}

AVISO = (
    "A projeção de peso é uma estimativa de um modelo simplificado (Hall et al., "
    "2011) e vale só para poucas semanas. Ela não considera a adaptação "
    "metabólica, a retenção de líquidos nem a variação individual."
)


def projetar_peso(  # noqa: PLR0913, PLR0917  assinatura fixa do contrato
    sexo: Sexo,
    idade: int,
    peso_kg: float,
    altura_cm: float,
    atividade: Atividade,
    kcal_dia: float,
    semanas: int = 8,
) -> list[float]:
    """peso no fim de cada semana, com o get ajustado ao peso da semana.

    So a serie de peso; o cenario ideal (kcal_dia = kcal total do plano) e a
    serie de adequacao sao montados no `Cenario` pela NS-046.

    Args:
        sexo: sexo biologico usado na equacao.
        idade: anos completos.
        peso_kg: peso inicial em kg.
        altura_cm: altura em cm.
        atividade: nivel de atividade fisica da ficha.
        kcal_dia: consumo medio do cenario em kcal/dia.
        semanas: quantas semanas projetar.

    Returns:
        pesos da semana 0 (peso inicial) ate `semanas`; len == semanas + 1.

    Raises:
        ValueError: kcal_dia ou semanas fora de FAIXAS, dados da ficha fora
            das faixas da energia ou peso projetado que sai delas.
    """
    for nome, valor in {"kcal_dia": kcal_dia, "semanas": semanas}.items():
        minimo, maximo = FAIXAS[nome]
        if not minimo <= valor <= maximo:
            raise ValueError(f"{nome}={valor} fora da faixa {minimo} a {maximo}")
    pesos = [peso_kg]
    for i in range(semanas):
        peso = pesos[-1]
        try:
            gasto = energia.get(sexo, idade, peso, altura_cm, atividade)
        except ValueError as e:
            if i == 0:
                raise
            # diz a semana para nao parecer erro da ficha
            msg = f"semana {i}: peso projetado {peso:.1f} kg fora da faixa"
            raise ValueError(msg) from e
        pesos.append(peso + 7 * (kcal_dia - gasto) / RHO_KCAL_KG)
    return pesos
