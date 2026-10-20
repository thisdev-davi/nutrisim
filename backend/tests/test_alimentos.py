from types import SimpleNamespace

from fastapi import status
from fastapi.testclient import TestClient

from app.api.alimentos import normalizar_busca
from app.db.deps import obter_sessao
from app.main import app


class ResultadoFalso:
    """Linhas simuladas de uma consulta SQLAlchemy."""

    @staticmethod
    def all():
        """Retorna um alimento com seus nutrientes.

        Returns:
            Lista com uma linha simulada.
        """
        return [
            SimpleNamespace(
                id=1,
                nome="Arroz, integral, cozido",
                categoria_id=1,
                kcal=124.0,
                proteina=2.6,
                carboidratos=25.8,
                lipidios=1.0,
                fibra_alimentar=2.7,
                sodio=1.0,
                gordura_saturada=0.3,
            )
        ]


class SessaoFalsa:
    """Sessão simulada para o teste do endpoint."""

    @staticmethod
    def execute(_consulta):
        """Retorna resultados simulados.

        Returns:
            Resultado simulado da consulta.
        """
        return ResultadoFalso()


def sessao_falsa():
    """Fornece uma sessão simulada ao endpoint.

    Yields:
        Sessão simulada.
    """
    yield SessaoFalsa()


def test_normalizar_busca_remove_acentos_e_maiusculas():
    """A normalização remove espaços, acentos e maiúsculas."""
    assert normalizar_busca("  ÁRROZ  ") == "arroz"


def test_busca_de_alimentos():
    """O endpoint retorna alimentos encontrados pelo nome."""
    app.dependency_overrides[obter_sessao] = sessao_falsa
    try:
        resposta = TestClient(app).get("/api/alimentos?nome=ARROZ")
    finally:
        app.dependency_overrides.clear()

    assert resposta.status_code == status.HTTP_200_OK
    assert resposta.json() == [
        {
            "id": 1,
            "nome": "Arroz, integral, cozido",
            "categoria_id": 1,
            "kcal": 124.0,
            "proteina": 2.6,
            "carboidratos": 25.8,
            "lipidios": 1.0,
            "fibra_alimentar": 2.7,
            "sodio": 1.0,
            "gordura_saturada": 0.3,
        }
    ]
