from types import SimpleNamespace

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.dialects import postgresql

from app.api.alimentos import normalizar_busca
from app.db.deps import obter_sessao
from app.main import app


class ResultadoFalso:
    """linhas simuladas de uma consulta SQLAlchemy."""

    @staticmethod
    def all():
        """retorna um alimento com seus nutrientes.

        Returns:
            lista com uma linha simulada.
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
    """sessao simulada que guarda a consulta recebida."""

    def execute(self, consulta):
        """guarda a consulta e devolve resultados simulados.

        Returns:
            resultado simulado da consulta.
        """
        self.consulta = consulta
        return ResultadoFalso()


def sessao_falsa():
    """fornece uma sessao simulada ao endpoint.

    Yields:
        sessao simulada.
    """
    yield SessaoFalsa()


def test_normalizar_busca_remove_acentos_e_maiusculas():
    """a normalizacao tira acento, maiuscula e espaco sobrando."""
    assert normalizar_busca("  ÁRROZ  ") == "arroz"
    assert normalizar_busca("Coco,  verde") == "coco, verde"


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


def test_busca_com_espacos_nao_consulta_o_banco():
    """retorna lista vazia sem consultar o banco para termo em branco."""
    class SessaoQueFalha:
        @staticmethod
        def execute(_consulta):
            raise AssertionError("a busca vazia nao deve consultar o banco")

    def sessao_falsa_vazia():
        yield SessaoQueFalha()

    app.dependency_overrides[obter_sessao] = sessao_falsa_vazia
    try:
        resposta = TestClient(app).get("/api/alimentos?nome=%20%20")
    finally:
        app.dependency_overrides.clear()

    assert resposta.status_code == status.HTTP_200_OK
    assert resposta.json() == []


def test_busca_escapa_coringas_do_like():
    """% e _ do termo vao escapados na consulta do endpoint."""
    sessao = SessaoFalsa()
    app.dependency_overrides[obter_sessao] = lambda: sessao
    try:
        TestClient(app).get("/api/alimentos?nome=a_b%25")
    finally:
        app.dependency_overrides.clear()

    sql = sessao.consulta.compile(dialect=postgresql.dialect())
    assert "ESCAPE" in str(sql)
    assert "a/_b/%" in sql.params.values()
