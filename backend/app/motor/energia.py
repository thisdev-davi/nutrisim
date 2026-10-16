# gasto energetico total (NS-024): funcao pura, sem ia
from typing import Literal

Sexo = Literal["feminino", "masculino"]
Atividade = Literal["sedentario", "leve", "moderado", "intenso"]

# fatores multiplicados pela tmb; atribuidos a McArdle et al. (1996), fonte a confirmar
FATORES_ATIVIDADE: dict[Atividade, float] = {
    "sedentario": 1.2,
    "leve": 1.375,
    "moderado": 1.55,
    "intenso": 1.725,
}

# faixas plausiveis; os limites sao aceitos
FAIXAS = {"idade": (18, 100), "peso_kg": (30, 300), "altura_cm": (120, 230)}


def _validar(**valores: float) -> None:
    for nome, valor in valores.items():
        minimo, maximo = FAIXAS[nome]
        if not minimo <= valor <= maximo:
            raise ValueError(f"{nome}={valor} fora da faixa {minimo} a {maximo}")


def tmb(sexo: Sexo, idade: int, peso_kg: float, altura_cm: float) -> float:
    """taxa metabolica basal por Mifflin-St Jeor (MIFFLIN et al., 1990).

    Entrada fora de FAIXAS gera ValueError.

    Args:
        sexo: sexo biologico usado na equacao.
        idade: anos completos.
        peso_kg: peso em kg.
        altura_cm: altura em cm.

    Returns:
        tmb em kcal/dia.
    """
    _validar(idade=idade, peso_kg=peso_kg, altura_cm=altura_cm)
    base = 10 * peso_kg + 6.25 * altura_cm - 5 * idade
    return base + (5 if sexo == "masculino" else -161)


def get(
    sexo: Sexo, idade: int, peso_kg: float, altura_cm: float, atividade: Atividade
) -> float:
    """gasto energetico total: tmb x fator de atividade.

    Args:
        sexo: sexo biologico usado na equacao.
        idade: anos completos.
        peso_kg: peso em kg.
        altura_cm: altura em cm.
        atividade: nivel de atividade fisica da ficha.

    Returns:
        get em kcal/dia.
    """
    return tmb(sexo, idade, peso_kg, altura_cm) * FATORES_ATIVIDADE[atividade]
