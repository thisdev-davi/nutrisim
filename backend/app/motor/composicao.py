from collections.abc import Mapping
from dataclasses import dataclass, field

NUTRIENTES = (
    "kcal",
    "proteina",
    "carboidratos",
    "lipidios",
    "fibra_alimentar",
    "sodio",
    "calcio",
    "ferro",
    "potassio",
    "vitamina_c",
)


@dataclass(frozen=True)
class Item:
    """alimento da TACO com a porção consumida.

    Attributes:
        nome: nome do alimento, usado nos avisos.
        gramas: porção em gramas.
        nutrientes: valores por 100 g; None (NA da TACO) ou ausente é dado faltante.
    """

    nome: str
    gramas: float
    nutrientes: Mapping[str, float | None]


@dataclass(frozen=True)
class Resultado:
    """soma dos nutrientes e dos alimentos sem dado.

    Attributes:
        valores: total de cada nutriente de NUTRIENTES.
        sem_dado: nutriente -> alimentos que entraram com 0 por falta de dado.
    """

    valores: dict[str, float]
    sem_dado: dict[str, list[str]] = field(default_factory=dict)


@dataclass(frozen=True)
class Composicao:
    """total do dia e valor de cada refeição."""

    total: Resultado
    por_refeicao: dict[str, Resultado]


def calcular_refeicao(itens: list[Item]) -> Resultado:
    """soma os nutrientes dos itens: valor por 100 g x gramas / 100.

    Dado faltante (None) conta como 0 e o alimento vai para `sem_dado`, para o
    total não parecer completo. O "Tr" da TACO já chega como 0.0. Porção zero
    não contribui nem gera aviso.

    Args:
        itens: alimentos com porção em gramas.

    Returns:
        totais de NUTRIENTES e os avisos de dado faltante.

    Raises:
        ValueError: se alguma porção for negativa.
    """
    valores = dict.fromkeys(NUTRIENTES, 0.0)
    sem_dado: dict[str, list[str]] = {}
    for item in itens:
        if item.gramas < 0:
            raise ValueError(f"{item.nome}: gramas={item.gramas} negativa")
        if item.gramas == 0:
            continue
        for nutriente in NUTRIENTES:
            por_100g = item.nutrientes.get(nutriente)
            if por_100g is None:
                sem_dado.setdefault(nutriente, []).append(item.nome)
            else:
                valores[nutriente] += por_100g * item.gramas / 100
    return Resultado(valores, sem_dado)


def calcular_composicao(refeicoes: Mapping[str, list[Item]]) -> Composicao:
    """total e valor por refeição.

    Args:
        refeicoes: nome da refeição -> itens consumidos nela.

    Returns:
        total do dia e o resultado de cada refeição.
    """
    por_refeicao = {nome: calcular_refeicao(itens) for nome, itens in refeicoes.items()}
    todos = [item for itens in refeicoes.values() for item in itens]
    return Composicao(calcular_refeicao(todos), por_refeicao)
