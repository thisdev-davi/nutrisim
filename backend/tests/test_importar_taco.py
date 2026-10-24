import pytest

from scripts.importar_taco import converter_float


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        ("Tr", 0.0),
        (" tr ", 0.0),
        ("NA", None),
        ("*", None),
        ("", None),
        (" ", None),
        ("1.5", 1.5),
    ],
)
def test_converter_float_trata_valores_da_taco(valor, esperado):
    """converte valores especiais da TACO para o tipo esperado."""
    assert converter_float(valor) == esperado
