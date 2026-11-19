import csv
import math
import re
from pathlib import Path

import pytest

from app.motor.precos import CSV_PRECOS, ler_precos, precos

TACO = Path(__file__).resolve().parents[1] / "data" / "taco" / "food.csv"
CABECALHO = "alimento_id,nome,preco_100g_reais,fonte,data_referencia\n"
MINIMO_DE_ALIMENTOS = 50
ARROZ_COZIDO = 3


def _taco() -> dict[int, str]:
    """le a TACO com o espaco duplo normalizado, como no importador.

    Returns:
        id -> nome do alimento.
    """
    with TACO.open(encoding="utf-8") as f:
        return {int(a["id"]): " ".join(a["name"].split()) for a in csv.DictReader(f)}


def test_todo_id_existe_na_taco_com_o_mesmo_nome():
    """o csv usa ids e nomes da TACO."""
    taco = _taco()
    with CSV_PRECOS.open(encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))

    assert len(linhas) >= MINIMO_DE_ALIMENTOS
    for linha in linhas:
        assert taco[int(linha["alimento_id"])] == linha["nome"]
        assert linha["fonte"]
        assert linha["data_referencia"]


def test_precos_positivos_e_finitos():
    """todo preco e um numero positivo."""
    assert all(math.isfinite(p) and p > 0 for p in precos().values())


@pytest.mark.parametrize(
    ("alimento_id", "esperado"),
    [
        (4, 4.09 / 1000 * 100),  # arroz, R$/kg
        (489, 10.20 / (12 * 55) * 100),  # ovo, R$/duzia de ovos de 55 g
        (458, 6.63 / 1030 * 100),  # leite, R$/litro a 1,03 g/ml
        (272, 7.97 / (900 * 0.92) * 100),  # oleo, R$/lata de 900 ml a 0,92 g/ml
        (41, 3.31 / 500 * 100),  # macarrao, R$/pacote de 500 g
    ],
)
def test_conversao_para_100g(alimento_id, esperado):
    """preco por kg, duzia, litro ou pacote vira preco por 100 g."""
    assert precos()[alimento_id] == pytest.approx(esperado, abs=1e-3)


def _gramas(unidade: str) -> float:
    """peso da unidade da coluna fonte, com as conversoes do modulo.

    Returns:
        gramas da unidade.
    """
    fixas = {"dúzia": 12 * 55, "litro": 1030, "lata de 900 ml": 900 * 0.92}
    if unidade in fixas:
        return fixas[unidade]
    if pacote := re.fullmatch(r"\w+ de (\d+) (g|kg)", unidade):
        return int(pacote[1]) * (1000 if pacote[2] == "kg" else 1)
    assert unidade.startswith("kg"), unidade
    return 1000


def test_toda_linha_bate_com_o_preco_original_da_fonte():
    """recalcula cada preco a partir do 'R$ x/unidade' da coluna fonte."""
    with CSV_PRECOS.open(encoding="utf-8") as f:
        for linha in csv.DictReader(f):
            original = re.search(r"R\$ ([\d,]+)/(.+)$", linha["fonte"])
            assert original, linha["fonte"]
            reais = float(original[1].replace(",", "."))
            esperado = reais / _gramas(original[2]) * 100
            assert float(linha["preco_100g_reais"]) == pytest.approx(esperado, abs=1e-4)


def test_tabela_e_somente_leitura():
    """escrever no resultado nao pode corromper o cache do processo."""
    with pytest.raises(TypeError):
        precos()[ARROZ_COZIDO] = 1.0


def test_alimento_sem_preco_fica_de_fora():
    """arroz cozido nao tem fonte de preco: o custo fica incompleto."""
    assert ARROZ_COZIDO not in precos()


@pytest.mark.parametrize("preco", ["0", "-1.5", "nan", "inf"])
def test_rejeita_preco_invalido(tmp_path, preco):
    """preco zero, negativo ou nao finito quebra a carga."""
    arquivo = tmp_path / "precos.csv"
    arquivo.write_text(CABECALHO + f"4,Arroz,{preco},teste,2026-09\n", encoding="utf-8")

    with pytest.raises(ValueError, match="4"):
        ler_precos(arquivo)


def test_rejeita_id_repetido(tmp_path):
    """dois precos para o mesmo alimento e erro de digitacao."""
    arquivo = tmp_path / "precos.csv"
    arquivo.write_text(
        CABECALHO + "4,Arroz,0.4,a,2026-09\n4,Arroz,0.5,b,2026-09\n", encoding="utf-8"
    )

    with pytest.raises(ValueError, match="repetido"):
        ler_precos(arquivo)
