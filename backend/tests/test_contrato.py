from fastapi import status
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app=app)


def test_criar_sessao_e_conversar():
    """fluxo do mock: cria a sessao e recebe a fala em sse."""
    sessao = client.post(
        "/api/sessoes", json={"perfil_id": "adulto-hipertensao", "dificuldade": "facil"}
    )
    assert sessao.status_code == status.HTTP_201_CREATED

    url = f"/api/sessoes/{sessao.json()['id']}/mensagens"
    linhas = client.post(url, json={"texto": "oi"}).text.splitlines()
    eventos = [linha for linha in linhas if linha.startswith("event:")]
    assert eventos[0] == "event: trecho"
    assert eventos[-1] == "event: fim"


def test_erros_no_formato_padrao():
    """todo erro sai como {"erro": {"codigo", "mensagem"}}."""
    nao_existe = client.get("/api/sessoes/nao-existe")
    assert nao_existe.status_code == status.HTTP_404_NOT_FOUND
    assert nao_existe.json()["erro"]["codigo"] == "sessao_nao_encontrada"

    invalido = client.post("/api/sessoes", json={})
    assert invalido.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert invalido.json()["erro"]["codigo"] == "dados_invalidos"
