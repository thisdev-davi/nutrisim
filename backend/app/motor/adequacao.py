# adequacao dos nutrientes as DRIs (NS-025): funcao pura, sem ia
#
# fontes:
# INSTITUTE OF MEDICINE. Dietary Reference Intakes: the essential guide to
# nutrient requirements. Washington, DC: The National Academies Press, 2006.
# INSTITUTE OF MEDICINE. Dietary Reference Intakes for calcium and vitamin D.
# Washington, DC: The National Academies Press, 2011.
# NATIONAL ACADEMIES OF SCIENCES, ENGINEERING, AND MEDICINE. Dietary Reference
# Intakes for sodium and potassium. Washington, DC: The National Academies Press,
# 2019.
# proteina, carboidratos, fibra, ferro e vitamina c seguem o guia de 2006; calcio
# usa a revisao de 2011 e sodio e potassio a de 2019, que substituem os de 2006.
# valores por dia, nas unidades da TACO (g para macronutrientes e fibra, mg para
# minerais e vitamina c). gestantes, lactantes e fumantes ficam fora.
#
# limites da classificacao, tirados da propria DRI (sem margem arbitraria):
#   abaixo:   consumo < referencia (RDA ou AI)
#   adequado: referencia <= consumo <= limite (sem limite definido, nao ha teto)
#   acima:    consumo > limite
# o limite e o UL; no sodio, que nao tem UL desde 2019, e a CDRR (2300 mg)
from dataclasses import dataclass
from typing import Literal

from app.motor.composicao import Resultado
from app.motor.energia import FAIXAS, Sexo

Tipo = Literal["RDA", "AI"]
Classificacao = Literal["abaixo", "adequado", "acima"]

# faixas etarias da DRI; a de 14-18 so recebe 18 anos, o minimo de FAIXAS
FAIXAS_ETARIAS = ("14-18", "19-30", "31-50", "51-70", "71+")
_IDADE_MAXIMA = (18, 30, 50, 70, FAIXAS["idade"][1])

# nutriente: (tipo, feminino, masculino, ul), cada tupla na ordem de FAIXAS_ETARIAS
# kcal (comparada ao GET da NS-024) e lipidios (so tem AMDR) nao tem RDA nem AI
_TABELA: dict[str, tuple[Tipo, tuple, tuple, tuple | None]] = {
    "proteina": ("RDA", (46, 46, 46, 46, 46), (52, 56, 56, 56, 56), None),
    "carboidratos": ("RDA", (130,) * 5, (130,) * 5, None),
    "fibra_alimentar": ("AI", (26, 25, 25, 21, 21), (38, 38, 38, 30, 30), None),
    "sodio": ("AI", (1500,) * 5, (1500,) * 5, (2300,) * 5),
    "calcio": (
        "RDA",
        (1300, 1000, 1000, 1200, 1200),
        (1300, 1000, 1000, 1000, 1200),
        (3000, 2500, 2500, 2000, 2000),
    ),
    "ferro": ("RDA", (15, 18, 18, 8, 8), (11, 8, 8, 8, 8), (45,) * 5),
    "potassio": (
        "AI",
        (2300, 2600, 2600, 2600, 2600),
        (3000, 3400, 3400, 3400, 3400),
        None,
    ),
    "vitamina_c": (
        "RDA",
        (65, 75, 75, 75, 75),
        (75, 90, 90, 90, 90),
        (1800, 2000, 2000, 2000, 2000),
    ),
}


@dataclass(frozen=True)
class Referencia:
    """valor de referência da DRI para um nutriente.

    Attributes:
        valor: RDA ou AI por dia, na unidade da TACO.
        tipo: "RDA" (ingestão recomendada) ou "AI" (ingestão adequada).
        ul: limite superior tolerável (UL), ou a CDRR no sódio; None quando
            não há limite definido.
    """

    valor: float
    tipo: Tipo
    ul: float | None = None


@dataclass(frozen=True)
class Adequacao:
    """consumo de um nutriente comparado à referência.

    Attributes:
        consumo: total do nutriente no dia.
        referencia: valor da DRI usado na comparação.
        percentual: consumo / referência x 100.
        classificacao: abaixo, adequado ou acima, pelos limites do módulo.
        sem_dado: alimentos com "NA" neste nutriente; o consumo pode estar
            subestimado.
    """

    consumo: float
    referencia: Referencia
    percentual: float
    classificacao: Classificacao
    sem_dado: list[str]


REFERENCIAS: dict[tuple[Sexo, str], dict[str, Referencia]] = {
    (sexo, faixa): {
        nutriente: Referencia(
            valores[indice_sexo][i], tipo, None if ul is None else ul[i]
        )
        for nutriente, (tipo, *valores, ul) in _TABELA.items()
    }
    for indice_sexo, sexo in enumerate(("feminino", "masculino"))
    for i, faixa in enumerate(FAIXAS_ETARIAS)
}


def faixa_etaria(idade: int) -> str:
    """faixa etária da DRI para a idade.

    Args:
        idade: anos completos, dentro de FAIXAS["idade"].

    Returns:
        uma das FAIXAS_ETARIAS.

    Raises:
        ValueError: idade fora de FAIXAS["idade"].
    """
    minimo, maximo = FAIXAS["idade"]
    if not minimo <= idade <= maximo:
        raise ValueError(f"idade={idade} fora da faixa {minimo} a {maximo}")
    return next(
        faixa
        for faixa, limite in zip(FAIXAS_ETARIAS, _IDADE_MAXIMA, strict=True)
        if idade <= limite
    )


def referencias(sexo: Sexo, idade: int) -> dict[str, Referencia]:
    """referências da DRI para o sexo e a idade.

    Args:
        sexo: sexo biológico.
        idade: anos completos.

    Returns:
        nutriente -> referência.

    Raises:
        ValueError: sexo desconhecido ou idade fora de FAIXAS["idade"].
    """
    if sexo not in {"feminino", "masculino"}:
        raise ValueError(f"sexo={sexo} desconhecido")
    return REFERENCIAS[sexo, faixa_etaria(idade)]


def classificar(consumo: float, referencia: Referencia) -> Classificacao:
    """abaixo, adequado ou acima, pelos limites do topo do módulo.

    Compara o consumo direto com a referência, e não o percentual, para o
    arredondamento não tirar um consumo igual à RDA de "adequado".

    Args:
        consumo: total do nutriente no dia.
        referencia: valor da DRI.

    Returns:
        a classificação.
    """
    if consumo < referencia.valor:
        return "abaixo"
    if referencia.ul is not None and consumo > referencia.ul:
        return "acima"
    return "adequado"


def calcular_adequacao(
    resultado: Resultado, sexo: Sexo, idade: int
) -> dict[str, Adequacao]:
    """adequação de cada nutriente com DRI ao total calculado pela composição.

    "Tr" já chega como 0.0 e entra na conta normalmente. "NA" também soma 0 na
    composição, mas o alimento segue em `sem_dado`, porque o "abaixo" pode vir
    da falta de dado e não do plano. Sexo e idade passam pela validação de
    `referencias`.

    Args:
        resultado: total do dia (ou de uma refeição) da composição.
        sexo: sexo biológico.
        idade: anos completos.

    Returns:
        nutriente -> adequação, para os nutrientes de REFERENCIAS.
    """
    adequacoes = {}
    for nutriente, referencia in referencias(sexo, idade).items():
        consumo = resultado.valores[nutriente]
        adequacoes[nutriente] = Adequacao(
            consumo,
            referencia,
            consumo / referencia.valor * 100,
            classificar(consumo, referencia),
            list(resultado.sem_dado.get(nutriente, [])),
        )
    return adequacoes
