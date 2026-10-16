from pathlib import Path

import pytest
from pydantic import ValidationError

from app.schemas.ficha import Ficha, Restricoes

EXEMPLO = Path(__file__).with_name("ficha_exemplo.json").read_text()


def test_exemplo_valida_e_paciente_nao_ve_gabarito():
    """o exemplo valida e a parte do paciente nao tem restricoes nem gabarito."""
    ficha = Ficha.model_validate_json(EXEMPLO)
    visivel = ficha.paciente.model_dump_json()
    assert "conduta_esperada" not in visivel
    assert "sodio_max_mg" not in visivel


def test_proteina_minima_acima_da_maxima_falha():
    """faixa invertida e rejeitada."""
    with pytest.raises(ValidationError):
        Restricoes(proteina_g_kg_min=1.5, proteina_g_kg_max=1.2)
