from fastapi import status
from fastapi.testclient import TestClient
from main import app

client = TestClient(app=app)


def test_health_check_returns_online():
    """Funcao responsavel por garantir que o endpoint /health esta no ar."""
    response = client.get("/health")

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {"status": "online"}

