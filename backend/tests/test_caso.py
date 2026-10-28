import json
from types import SimpleNamespace

import httpx
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from google.genai._gaos.lib.compat_errors import (  # noqa: PLC2701
    BadRequestError,
    InternalServerError,
)

from app.db.modelos import ChamadaLLM, Sessao
from app.llm import cliente
from app.main import app
from tests.test_cliente_llm import provedor_falso
from tests.test_ficha import EXEMPLO

# as rotas da simulacao exigem login (NS-035)
pytestmark = pytest.mark.usefixtures("usuario")

client = TestClient(app=app)
NOVA = {"perfil_id": "adulto-dislipidemia", "dificuldade": "dificil"}


def textos_ocultos(ficha: dict) -> list[str]:
    """trechos da ficha que o estudante nunca pode ver.

    Returns:
        textos de omissoes, imprecisoes, recordatorio, restricoes e gabarito.
    """
    paciente = ficha["paciente"]
    return [
        *(o["informacao"] for o in paciente["omissoes"]),
        *paciente["imprecisoes"],
        *paciente["recordatorio"],
        *ficha["restricoes"]["alimentos_evitados"],
        *ficha["gabarito"]["o_que_investigar"],
        "conduta_esperada",
        "sodio_max_mg",
    ]


def test_cria_o_caso_sem_vazar_a_ficha(monkeypatch, banco):
    """a ficha fica no banco; post e get devolvem so o que o estudante ve."""
    provedor_falso(monkeypatch, [EXEMPLO])
    criada = client.post("/api/sessoes", json=NOVA)
    assert criada.status_code == status.HTTP_201_CREATED
    sessao = criada.json()
    assert sessao["paciente"] == {
        "nome": "Carlos",
        "idade": 52,
        "queixa_principal": "pressão alta e dificuldade para perder peso",
    }
    assert sessao["etapa"] == "anamnese"
    assert sessao["mensagens"] == []

    obtida = client.get(f"/api/sessoes/{sessao['id']}")
    assert obtida.json() == sessao

    # o exemplo e de hipertensao: o perfil pedido vence o que o llm devolveu
    (linha,) = [o for o in banco.objetos if isinstance(o, Sessao)]
    assert linha.ficha["perfil_id"] == sessao["perfil_id"] == NOVA["perfil_id"]
    assert linha.ficha["dificuldade"] == sessao["dificuldade"] == NOVA["dificuldade"]
    assert linha.ficha["restricoes"]["sodio_max_mg"] is None
    assert linha.ficha["restricoes"]["gordura_saturada_max_pct_vet"] == 10  # noqa: PLR2004

    for oculto in textos_ocultos(json.loads(EXEMPLO)):
        assert oculto not in criada.text
        assert oculto not in obtida.text


def test_perfil_de_encaminhamento_impoe_a_conduta(monkeypatch, banco):
    """a conduta esperada vem do perfil, nao do llm."""
    provedor_falso(monkeypatch, [EXEMPLO])
    nova = {"perfil_id": "adulto-jovem-emagrecimento", "dificuldade": "medio"}
    criada = client.post("/api/sessoes", json=nova)
    assert criada.status_code == status.HTTP_201_CREATED
    (linha,) = [o for o in banco.objetos if isinstance(o, Sessao)]
    assert linha.ficha["gabarito"]["conduta_esperada"] == "encaminhamento"
    assert linha.ficha["restricoes"]["sodio_max_mg"] is None


@pytest.mark.parametrize(
    ("perfil_id", "evitados"),
    [
        ("adulto-diabetes-tipo2", ["bebidas adoçadas", "doces"]),
        ("adulto-hipertensao", []),
        ("adulto-dislipidemia", []),
        ("idoso-baixa-ingestao", []),
        ("adulto-jovem-emagrecimento", []),
    ],
)
def test_alimentos_evitados_vem_do_perfil(monkeypatch, banco, perfil_id, evitados):
    """o llm punha comportamentos na lista; o motor so casa nome de alimento."""
    provedor_falso(monkeypatch, [EXEMPLO])
    nova = {"perfil_id": perfil_id, "dificuldade": "facil"}
    assert client.post("/api/sessoes", json=nova).status_code == status.HTTP_201_CREATED
    (linha,) = [o for o in banco.objetos if isinstance(o, Sessao)]
    assert linha.ficha["restricoes"]["alimentos_evitados"] == evitados


def test_llm_sem_saida_valida_da_503_e_guarda_os_tokens(monkeypatch, banco):
    """sem ficha valida nao cria sessao, mas registra o que foi gasto."""
    provedor_falso(monkeypatch, ["nao e json"] * cliente.TENTATIVAS)
    resposta = client.post("/api/sessoes", json=NOVA)
    assert resposta.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert resposta.json()["erro"]["codigo"] == "caso_nao_gerado"
    assert all(isinstance(o, ChamadaLLM) for o in banco.objetos)
    assert len(banco.objetos) == cliente.TENTATIVAS
    assert banco.commits == 1


def provedor_com_erro(monkeypatch, erro, codigo_http):
    """troca o gemini por um que sempre responde com o erro."""
    resposta = httpx.Response(codigo_http, request=httpx.Request("POST", "x"))

    def create(**_):
        raise erro("falha", response=resposta, body=None)

    falso = SimpleNamespace(interactions=SimpleNamespace(create=create))
    monkeypatch.setattr(cliente, "_cliente", lambda: falso)
    monkeypatch.setenv("LLM_MODELO", "modelo-teste")


@pytest.mark.usefixtures("banco")
def test_gemini_sobrecarregado_da_503(monkeypatch):
    """5xx do provedor e passageiro: o front oferece tentar de novo."""
    provedor_com_erro(monkeypatch, InternalServerError, 503)
    resposta = client.post("/api/sessoes", json=NOVA)
    assert resposta.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert resposta.json()["erro"]["codigo"] == "caso_nao_gerado"


@pytest.mark.usefixtures("banco")
def test_erro_4xx_do_provedor_continua_500(monkeypatch):
    """4xx e bug nosso (schema, chave): nao pode se passar por sobrecarga."""
    provedor_com_erro(monkeypatch, BadRequestError, 400)
    resposta = client.post("/api/sessoes", json=NOVA)
    assert resposta.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
