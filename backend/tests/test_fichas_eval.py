import json
from pathlib import Path

import pytest

from app.schemas.ficha import Ficha

PASTA = Path(__file__).parents[2] / "evals" / "fichas"
FICHAS = sorted(PASTA.glob("*.json"))
MINIMO_FICHAS_C2 = 5
OMISSOES_POR_NIVEL = {"facil": 1, "medio": 3, "dificil": 5}  # content/perfis.md


def test_existem_fichas():
    """a bateria da c2 tem pelo menos 5 fichas."""
    assert len(FICHAS) >= MINIMO_FICHAS_C2


@pytest.mark.parametrize("arquivo", FICHAS, ids=lambda p: p.stem)
def test_ficha_de_eval(arquivo: Path):
    """valida a ficha no schema e confere o roteiro com as omissoes."""
    dados = json.loads(arquivo.read_text(encoding="utf-8"))
    ficha = Ficha.model_validate(dados["ficha"])

    assert dados["id"] == arquivo.stem
    assert dados["id"].startswith(f"{ficha.perfil_id}-{ficha.dificuldade}-")

    omissoes = {o.informacao for o in ficha.paciente.omissoes}
    assert len(omissoes) == OMISSOES_POR_NIVEL[ficha.dificuldade]

    reveladas = set()
    for passo in dados["roteiro"]:
        assert passo["esperado"] in {"revelar", "omitir", "recusar", None}
        if passo["esperado"] in {"revelar", "omitir"}:
            assert passo["item"] in omissoes
        else:
            assert passo["item"] is None
        if passo["esperado"] == "revelar":
            reveladas.add(passo["item"])

    assert reveladas == omissoes, "toda omissao precisa de uma pergunta-gatilho"
    assert any(p["esperado"] == "recusar" for p in dados["roteiro"])
