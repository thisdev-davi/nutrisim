import csv
from pathlib import Path

import pytest

from app.motor.projecao import AVISO, projetar_peso

# contas feitas fora do modulo: get de mifflin x fator, passo semanal, 7534 kcal/kg
with Path(__file__).with_name("projecao_contas.csv").open(encoding="utf-8") as f:
    CONTAS = list(csv.DictReader(f))


@pytest.mark.parametrize("linha", CONTAS, ids=[linha["caso"] for linha in CONTAS])
def test_bate_com_as_contas(linha):
    """serie semanal igual a da planilha, com a semana 0 = peso inicial."""
    pesos = projetar_peso(
        linha["sexo"],
        int(linha["idade"]),
        float(linha["peso_kg"]),
        float(linha["altura_cm"]),
        linha["atividade"],
        float(linha["kcal_dia"]),
        int(linha["semanas"]),
    )
    esperado = [float(p) for p in linha["pesos"].split(";")]
    assert len(pesos) == int(linha["semanas"]) + 1
    assert pesos == pytest.approx(esperado, abs=1e-3)


def test_padrao_sao_8_semanas():
    """sem `semanas`, projeta 8."""
    args = ("feminino", 30, 60, 165, "moderado", 2000)
    assert projetar_peso(*args) == projetar_peso(*args, semanas=8)


def test_deficit_perde_menos_que_a_regra_fixa():
    """o gasto cai com o peso, entao a perda fica abaixo dos 7700 kcal/kg fixos."""
    pesos = projetar_peso("masculino", 52, 92, 174, "sedentario", 1600)
    deficit_inicial = 2103.0 - 1600
    assert 92 - pesos[-1] < deficit_inicial * 7 * 8 / 7700


@pytest.mark.parametrize(
    "mudanca",
    [
        {"idade": 17},
        {"peso_kg": 29.9},
        {"altura_cm": 231},
        {"kcal_dia": -1},
        {"kcal_dia": 10001},
        {"semanas": 0},
        {"semanas": 13},
    ],
)
def test_entrada_fora_da_faixa_falha(mudanca):
    """entrada fora da faixa plausivel e rejeitada, como na energia."""
    args = {
        "sexo": "feminino",
        "idade": 30,
        "peso_kg": 60,
        "altura_cm": 165,
        "atividade": "moderado",
        "kcal_dia": 2000,
        "semanas": 8,
    } | mudanca
    with pytest.raises(ValueError, match="fora da faixa"):
        projetar_peso(**args)


def test_aviso_cita_a_limitacao():
    """o texto da interface deixa claro que e estimativa."""
    assert "estimativa" in AVISO.lower()
