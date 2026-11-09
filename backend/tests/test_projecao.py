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
    # get inicial: mifflin 1752.5 x 1.2 (sedentario)
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


@pytest.mark.parametrize(
    ("kcal_dia", "semanas"), [(0, 1), (10000, 1), (2000, 1), (2000, 12)]
)
def test_bordas_das_faixas_sao_aceitas(kcal_dia, semanas):
    """os limites de FAIXAS entram."""
    pesos = projetar_peso("feminino", 30, 60, 165, "moderado", kcal_dia, semanas)
    assert len(pesos) == semanas + 1


def test_peso_projetado_fora_da_faixa_cita_a_semana():
    """o erro no meio da projecao diz em que semana o peso saiu da faixa."""
    with pytest.raises(ValueError, match="semana"):
        projetar_peso("feminino", 30, 30.5, 165, "moderado", 0, 12)
