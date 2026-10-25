import csv
from pathlib import Path

import pytest

from app.motor.adequacao import (
    FAIXAS_ETARIAS,
    REFERENCIAS,
    calcular_adequacao,
    faixa_etaria,
    referencias,
)
from app.motor.composicao import NUTRIENTES, Item, Resultado, calcular_composicao

# planilha com as contas feitas a mao (referencias de IOM 2006, 2011 e NASEM 2019)
with Path(__file__).with_name("adequacao_contas.csv").open(encoding="utf-8") as f:
    CONTAS = list(csv.DictReader(f))


def _resultado(**valores: float) -> Resultado:
    """total do dia com zero nos nutrientes nao informados.

    Args:
        **valores: nutriente -> total.

    Returns:
        resultado sem avisos de dado faltante.
    """
    return Resultado(dict.fromkeys(NUTRIENTES, 0.0) | valores)


@pytest.mark.parametrize("linha", CONTAS)
def test_bate_com_as_contas_a_mao(linha):
    """faixa, referencia, percentual e classificacao iguais aos da planilha."""
    idade = int(linha["idade"])
    resultado = _resultado(**{linha["nutriente"]: float(linha["consumo"])})

    adequacao = calcular_adequacao(resultado, linha["sexo"], idade)[linha["nutriente"]]

    assert faixa_etaria(idade) == linha["faixa"]
    assert adequacao.referencia.tipo == linha["tipo"]
    assert adequacao.referencia.valor == float(linha["referencia"])
    ul = float(linha["ul"]) if linha["ul"] else None
    assert adequacao.referencia.ul == ul
    assert adequacao.percentual == pytest.approx(float(linha["percentual"]))
    assert adequacao.classificacao == linha["classificacao"]


@pytest.mark.parametrize(
    ("idade", "faixa"),
    [
        (18, "14-18"),
        (19, "19-30"),
        (30, "19-30"),
        (31, "31-50"),
        (50, "31-50"),
        (51, "51-70"),
        (70, "51-70"),
        (71, "71+"),
        (100, "71+"),
    ],
)
def test_faixa_etaria_nos_limites(idade, faixa):
    """cada limite de faixa cai na faixa certa da DRI."""
    assert faixa_etaria(idade) == faixa


@pytest.mark.parametrize("idade", [17, 101])
def test_idade_fora_da_faixa_falha(idade):
    """mesma faixa de idade do GET (NS-024)."""
    with pytest.raises(ValueError, match="fora da faixa"):
        calcular_adequacao(_resultado(), "feminino", idade)


def test_sexo_desconhecido_falha():
    """sexo fora do Literal nao cai em nenhuma tabela por engano."""
    with pytest.raises(ValueError, match="desconhecido"):
        referencias("outro", 30)


def test_tabela_completa_e_coerente():
    """toda faixa tem os 8 nutrientes e nenhum UL fica abaixo da referencia."""
    nutrientes = {
        "proteina",
        "carboidratos",
        "fibra_alimentar",
        "sodio",
        "calcio",
        "ferro",
        "potassio",
        "vitamina_c",
    }
    assert len(REFERENCIAS) == 2 * len(FAIXAS_ETARIAS)
    for tabela in REFERENCIAS.values():
        assert set(tabela) == nutrientes
        for referencia in tabela.values():
            assert referencia.valor > 0
            assert referencia.ul is None or referencia.ul >= referencia.valor


def test_kcal_e_lipidios_ficam_de_fora():
    """sem RDA nem AI: energia vai contra o GET e lipidios so tem AMDR."""
    adequacao = calcular_adequacao(_resultado(kcal=2000, lipidios=70), "feminino", 30)

    assert "kcal" not in adequacao
    assert "lipidios" not in adequacao


def test_traco_conta_como_zero_sem_aviso():
    """'Tr' (0.0) da vitamina c do feijao: 0 % e abaixo, mas sem aviso."""
    feijao = Item("Feijão, carioca, cozido", 100, {"vitamina_c": 0.0})
    total = calcular_composicao({"almoco": [feijao]}).total

    vitamina_c = calcular_adequacao(total, "feminino", 30)["vitamina_c"]

    assert vitamina_c.consumo == 0
    assert vitamina_c.percentual == 0
    assert vitamina_c.classificacao == "abaixo"
    assert vitamina_c.sem_dado == []


def test_na_avisa_que_o_consumo_pode_estar_subestimado():
    """'NA' do arroz soma 0 e o alimento segue no aviso da adequacao.

    Contas: banana 21.6 * 120 / 100 = 25.92 mg; 25.92 / 75 * 100 = 34.56 %.
    """
    arroz = Item("Arroz, integral, cozido", 150, {"vitamina_c": None})
    banana = Item("Banana, prata, crua", 120, {"vitamina_c": 21.6})
    total = calcular_composicao({"almoco": [arroz], "lanche": [banana]}).total

    vitamina_c = calcular_adequacao(total, "feminino", 30)["vitamina_c"]

    assert vitamina_c.consumo == pytest.approx(25.92)
    assert vitamina_c.percentual == pytest.approx(34.56)
    assert vitamina_c.classificacao == "abaixo"
    assert vitamina_c.sem_dado == [arroz.nome]


def test_nutriente_so_com_na():
    """todos os alimentos sem dado: 0 %, abaixo e todos listados no aviso."""
    arroz = Item("Arroz, integral, cozido", 150, {"vitamina_c": None})
    pao = Item("Pão, trigo, francês", 50, {})

    vitamina_c = calcular_adequacao(
        calcular_composicao({"cafe": [pao], "almoco": [arroz]}).total,
        "masculino",
        40,
    )["vitamina_c"]

    assert vitamina_c.percentual == 0
    assert vitamina_c.classificacao == "abaixo"
    assert vitamina_c.sem_dado == [pao.nome, arroz.nome]


def test_aviso_e_copia_do_resultado():
    """mexer no aviso da adequacao nao altera o resultado da composicao."""
    resultado = Resultado(dict.fromkeys(NUTRIENTES, 0.0), {"ferro": ["Arroz"]})

    calcular_adequacao(resultado, "feminino", 30)["ferro"].sem_dado.append("Feijão")

    assert resultado.sem_dado["ferro"] == ["Arroz"]
