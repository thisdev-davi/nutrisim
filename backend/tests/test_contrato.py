import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.db.deps import obter_sessao
from app.main import app
from tests.test_cliente_llm import provedor_falso
from tests.test_ficha import EXEMPLO

client = TestClient(app=app)


@pytest.mark.usefixtures("banco")
def test_criar_sessao_e_conversar(monkeypatch):
    """cria a sessao com o llm falso e recebe a fala em sse."""
    provedor_falso(monkeypatch, [EXEMPLO])
    sessao = client.post(
        "/api/sessoes", json={"perfil_id": "adulto-hipertensao", "dificuldade": "facil"}
    )
    assert sessao.status_code == status.HTTP_201_CREATED

    url = f"/api/sessoes/{sessao.json()['id']}/mensagens"
    em_branco = client.post(url, json={"texto": "   "})
    assert em_branco.json()["erro"]["codigo"] == "dados_invalidos"

    linhas = client.post(url, json={"texto": "oi"}).text.splitlines()
    eventos = [linha for linha in linhas if linha.startswith("event:")]
    assert eventos[0] == "event: trecho"
    assert eventos[-1] == "event: fim"


@pytest.mark.usefixtures("banco")
def test_erros_no_formato_padrao():
    """todo erro sai como {"erro": {"codigo", "mensagem"}}."""
    nao_existe = client.get("/api/sessoes/nao-existe")
    assert nao_existe.status_code == status.HTTP_404_NOT_FOUND
    assert nao_existe.json()["erro"]["codigo"] == "sessao_nao_encontrada"

    invalido = client.post("/api/sessoes", json={})
    assert invalido.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert invalido.json()["erro"]["codigo"] == "dados_invalidos"


def test_erro_interno_e_405_mantem_cabecalhos():
    """o 500 leva o cors (senao o navegador bloqueia) e o 405 leva o Allow."""

    def banco_fora():
        raise RuntimeError("banco fora")

    origem = {"Origin": "http://localhost:3000"}
    app.dependency_overrides[obter_sessao] = banco_fora
    try:
        falha = client.get("/api/alimentos?nome=arroz", headers=origem)
    finally:
        app.dependency_overrides.clear()
    assert falha.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert falha.json()["erro"]["codigo"] == "erro_interno"
    assert falha.headers["access-control-allow-origin"] == origem["Origin"]

    metodo = client.delete("/api/perfis")
    assert metodo.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "GET" in metodo.headers["allow"]
