import json
from uuid import uuid4

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.api import plano
from app.db.modelos import Sessao
from app.main import app
from tests.test_cenario import PLANO, carregar
from tests.test_ficha import EXEMPLO

pytestmark = pytest.mark.usefixtures("usuario")

client = TestClient(app=app)

# carlos da ficha de exemplo: mifflin (920 + 1087,5 - 260 + 5) x 1,2 sedentario
GET_KCAL = 2103.0


@pytest.fixture(autouse=True)
def taco(monkeypatch):
    """TACO e precos em memoria: so o arroz tem preco (R$ 0,50 por 100 g)."""
    # como o banco, id fora da TACO so nao volta
    monkeypatch.setattr(
        plano, "carregar_taco", lambda db, ids: carregar(db, ids & {1, 2, 3})
    )
    monkeypatch.setattr(plano, "precos", lambda: {1: 0.5})


def nova_sessao(banco, usuario, etapa="plano", plano_salvo=None) -> Sessao:
    """sessao do estudante na etapa pedida.

    Returns:
        sessao gravada no banco falso.
    """
    sessao = Sessao(
        id=uuid4(),
        usuario_id=usuario.id,
        perfil_id="adulto-hipertensao",
        dificuldade="medio",
        etapa=etapa,
        ficha=json.loads(EXEMPLO),
        plano=plano_salvo,
    )
    banco.add(sessao)
    return sessao


def url(sessao, sufixo=""):
    """url do plano da sessao.

    Returns:
        caminho da rota.
    """
    return f"/api/sessoes/{sessao.id}/plano{sufixo}"


def test_put_calcula_grava_e_get_recalcula(banco, usuario):
    """os numeros saem do motor; o banco guarda so ids e gramas."""
    sessao = nova_sessao(banco, usuario)
    resposta = client.put(url(sessao), json=PLANO)
    assert resposta.status_code == status.HTTP_200_OK
    corpo = resposta.json()
    almoco, jantar = corpo["refeicoes"]
    assert [i["nome"] for i in almoco["itens"]] == ["Arroz", "Feijao"]
    assert [i["kcal"] for i in almoco["itens"]] == [200, 80]
    assert almoco["composicao"]["valores"]["kcal"] == 280  # noqa: PLR2004
    assert jantar["composicao"]["valores"]["kcal"] == 100  # noqa: PLR2004
    assert corpo["total"]["valores"]["kcal"] == 380  # noqa: PLR2004
    assert "Arroz" in corpo["total"]["sem_dado"]["sodio"]  # ausente na taco falsa
    assert corpo["get_kcal"] == pytest.approx(GET_KCAL)
    assert corpo["adequacao"]["proteina"]["consumo"] == pytest.approx(12.3)
    assert corpo["custo_diario_reais"] == pytest.approx(1.5)  # 300 g de arroz
    assert corpo["sem_preco"] == ["Feijao"]
    assert corpo["violacoes"] == []
    assert sessao.plano == PLANO
    assert banco.commits == 1

    assert client.get(url(sessao)).json() == corpo


def test_get_antes_do_put_da_404(banco, usuario):
    """a tela abre vazia antes do primeiro put."""
    resposta = client.get(url(nova_sessao(banco, usuario)))
    assert resposta.status_code == status.HTTP_404_NOT_FOUND
    assert resposta.json()["erro"]["codigo"] == "plano_nao_encontrado"


def test_alimento_fora_da_taco_da_422_e_nao_grava(banco, usuario):
    """id inexistente nao chega ao banco."""
    sessao = nova_sessao(banco, usuario)
    invalido = {
        "refeicoes": [{"nome": "Ceia", "itens": [{"alimento_id": 99, "gramas": 10}]}]
    }
    resposta = client.put(url(sessao), json=invalido)
    assert resposta.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert resposta.json()["erro"]["codigo"] == "alimento_invalido"
    assert sessao.plano is None


@pytest.mark.parametrize("gramas", [0, -5])
def test_porcao_nao_positiva_da_422(banco, usuario, gramas):
    """porcao zero ou negativa barra no schema."""
    corpo = {
        "refeicoes": [{"nome": "Ceia", "itens": [{"alimento_id": 1, "gramas": gramas}]}]
    }
    resposta = client.put(url(nova_sessao(banco, usuario)), json=corpo)
    assert resposta.json()["erro"]["codigo"] == "dados_invalidos"


@pytest.mark.parametrize("etapa", ["anamnese", "cenarios", "retorno"])
def test_put_fora_da_etapa_da_409(banco, usuario, etapa):
    """so a etapa plano aceita mudancas."""
    resposta = client.put(url(nova_sessao(banco, usuario, etapa)), json=PLANO)
    assert resposta.status_code == status.HTTP_409_CONFLICT
    assert resposta.json()["erro"]["codigo"] == "etapa_invalida"


def test_encerrar_sem_plano_da_404(banco, usuario):
    """nao ha o que encerrar antes do primeiro put."""
    resposta = client.post(url(nova_sessao(banco, usuario), "/encerrar"))
    assert resposta.json()["erro"]["codigo"] == "plano_nao_encontrado"


def test_encerrar_trava_o_plano(banco, usuario):
    """depois de encerrar, o put responde 409."""
    sessao = nova_sessao(banco, usuario, plano_salvo=PLANO)
    resposta = client.post(url(sessao, "/encerrar"))
    assert resposta.json() == {"etapa": "cenarios"}
    assert sessao.etapa == "cenarios"
    assert client.put(url(sessao), json=PLANO).status_code == status.HTTP_409_CONFLICT
    assert client.post(url(sessao, "/encerrar")).status_code == status.HTTP_409_CONFLICT


def test_encaminhar_grava_o_motivo_e_pula_os_cenarios(banco, usuario):
    """o plano salvo fica, mas a sessao vai direto ao retorno."""
    sessao = nova_sessao(banco, usuario, plano_salvo=PLANO)
    resposta = client.post(
        url(sessao, "/encaminhar"), json={"motivo": "  nefrologista "}
    )
    assert resposta.json() == {"etapa": "retorno"}
    assert sessao.encaminhamento == "nefrologista"
    assert sessao.etapa == "retorno"
    assert sessao.plano == PLANO
    assert banco.commits == 1

    de_novo = client.post(url(sessao, "/encaminhar"), json={"motivo": "outro"})
    assert de_novo.json()["erro"]["codigo"] == "etapa_invalida"


def test_encaminhar_sem_motivo_da_422(banco, usuario):
    """motivo em branco nao conta."""
    resposta = client.post(
        url(nova_sessao(banco, usuario), "/encaminhar"), json={"motivo": "  "}
    )
    assert resposta.json()["erro"]["codigo"] == "dados_invalidos"


def test_encerrar_anamnese_grava_a_etapa(banco, usuario):
    """a sessao passa ao plano uma vez so."""
    sessao = nova_sessao(banco, usuario, "anamnese")
    rota = f"/api/sessoes/{sessao.id}/anamnese/encerrar"
    assert client.post(rota).json() == {"etapa": "plano"}
    assert sessao.etapa == "plano"
    assert banco.commits == 1
    de_novo = client.post(rota)
    assert de_novo.status_code == status.HTTP_409_CONFLICT
    assert de_novo.json()["erro"]["codigo"] == "etapa_invalida"


def test_put_devolve_as_violacoes_do_motor(banco, usuario):
    """as restricoes da NS-044 chegam na resposta do PUT."""
    sessao = nova_sessao(banco, usuario)
    sessao.ficha["paciente"]["orcamento_mensal_reais"] = 30  # R$ 1/dia
    violacoes = client.put(url(sessao), json=PLANO).json()["violacoes"]
    assert [v["tipo"] for v in violacoes] == ["orcamento"]  # custo de R$ 1,50/dia
