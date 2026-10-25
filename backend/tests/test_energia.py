import csv
from pathlib import Path

import pytest

from app.motor.energia import get, tmb

# planilha com as contas feitas a mao (ultimas duas linhas sao os limites das faixas)
with Path(__file__).with_name("energia_contas.csv").open(encoding="utf-8") as f:
    CONTAS = list(csv.DictReader(f))


@pytest.mark.parametrize("linha", CONTAS)
def test_bate_com_as_contas_a_mao(linha):
    """tmb e get iguais aos da planilha."""
    args = (linha["sexo"], int(linha["idade"]))
    args += (float(linha["peso_kg"]), float(linha["altura_cm"]))
    assert tmb(*args) == pytest.approx(float(linha["tmb"]))
    assert get(*args, linha["atividade"]) == pytest.approx(float(linha["get"]))


@pytest.mark.parametrize(
    ("idade", "peso_kg", "altura_cm"),
    [(17, 70, 170), (101, 70, 170), (40, 29.9, 170), (40, 301, 170), (40, 70, 119)],
)
def test_fora_da_faixa_falha(idade, peso_kg, altura_cm):
    """entrada fora da faixa plausivel e rejeitada."""
    with pytest.raises(ValueError, match="fora da faixa"):
        tmb("feminino", idade, peso_kg, altura_cm)
