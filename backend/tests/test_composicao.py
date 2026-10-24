import csv
from pathlib import Path

import pytest

from app.motor.composicao import (
    NUTRIENTES,
    Item,
    calcular_composicao,
    calcular_refeicao,
)

# planilha com as contas feitas a mao (valores por 100 g de data/taco/nutrients.csv)
CONTAS = list(csv.DictReader(Path(__file__).with_name("composicao_contas.csv").open()))


@pytest.mark.parametrize("linha", CONTAS)
def test_bate_com_as_contas_a_mao(linha):
    """cada nutriente de um alimento igual ao da planilha."""
    item = Item(
        linha["alimento"],
        float(linha["gramas"]),
        {linha["nutriente"]: float(linha["por_100g"])},
    )

    valores = calcular_refeicao([item]).valores

    assert valores[linha["nutriente"]] == pytest.approx(float(linha["resultado"]))


def test_total_e_por_refeicao():
    """total do dia soma as refeicoes (contas: 186 + 76 = 262; 262 + 98 = 360)."""
    arroz = Item("Arroz, integral, cozido", 150, {"kcal": 124})
    feijao = Item("Feijão, carioca, cozido", 100, {"kcal": 76})
    banana = Item("Banana, prata, crua", 100, {"kcal": 98})

    composicao = calcular_composicao({"almoco": [arroz, feijao], "lanche": [banana]})

    assert composicao.por_refeicao["almoco"].valores["kcal"] == pytest.approx(262)
    assert composicao.por_refeicao["lanche"].valores["kcal"] == pytest.approx(98)
    assert composicao.total.valores["kcal"] == pytest.approx(360)


def test_porcao_zero_nao_contribui_nem_avisa():
    """porcao zero gera 0 em tudo e nenhum aviso, mesmo com dado faltante."""
    arroz = Item("Arroz, integral, cozido", 0, {"kcal": 124, "vitamina_c": None})

    resultado = calcular_refeicao([arroz])

    assert resultado.valores == dict.fromkeys(NUTRIENTES, 0.0)
    assert resultado.sem_dado == {}


def test_traco_conta_como_zero_sem_aviso():
    """'Tr' chega como 0.0: soma 0 e nao e dado faltante (vitamina c do feijao)."""
    feijao = Item("Feijão, carioca, cozido", 100, {"vitamina_c": 0.0})

    resultado = calcular_refeicao([feijao])

    assert resultado.valores["vitamina_c"] == 0
    assert "vitamina_c" not in resultado.sem_dado


def test_na_conta_como_zero_e_avisa():
    """'NA' (None ou ausente) soma 0 e lista o alimento no nutriente.

    A vitamina c do arroz integral cozido esta vazia na TACO (None no import).
    """
    arroz = Item("Arroz, integral, cozido", 100, {"kcal": 124, "vitamina_c": None})
    feijao = Item("Feijão, carioca, cozido", 100, {"kcal": 76, "vitamina_c": 0.0})

    resultado = calcular_refeicao([arroz, feijao])

    assert resultado.valores["kcal"] == pytest.approx(200)
    assert resultado.valores["vitamina_c"] == 0
    assert resultado.sem_dado["vitamina_c"] == ["Arroz, integral, cozido"]
    assert resultado.sem_dado["ferro"] == [arroz.nome, feijao.nome]
    assert "kcal" not in resultado.sem_dado


def test_na_aparece_no_total_do_dia():
    """aviso de dado faltante aparece no total e na refeicao de origem."""
    arroz = Item("Arroz, integral, cozido", 150, {"kcal": 124, "vitamina_c": None})

    composicao = calcular_composicao({"almoco": [arroz]})

    assert composicao.total.sem_dado["vitamina_c"] == [arroz.nome]
    assert composicao.por_refeicao["almoco"].sem_dado["vitamina_c"] == [arroz.nome]


def test_sem_itens_retorna_zero():
    """lista vazia devolve zeros."""
    assert calcular_refeicao([]).valores == dict.fromkeys(NUTRIENTES, 0.0)
    assert calcular_composicao({}).total.valores == dict.fromkeys(NUTRIENTES, 0.0)


def test_porcao_negativa_falha():
    """gramas negativas sao rejeitadas."""
    with pytest.raises(ValueError, match="negativa"):
        calcular_refeicao([Item("Arroz, integral, cozido", -1, {"kcal": 124})])
