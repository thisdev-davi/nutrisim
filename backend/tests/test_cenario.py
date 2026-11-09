import json
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from google.genai._gaos.lib.compat_errors import InternalServerError  # noqa: PLC2701
from google.genai._gaos.types.interactions import FunctionCallStep  # noqa: PLC2701

from app.db.modelos import ChamadaLLM, Sessao
from app.llm import cenario, cliente
from app.main import app
from tests.test_caso import provedor_com_erro
from tests.test_cliente_llm import RACIOCINIO, SAIDA, TOKENS, USO
from tests.test_ficha import EXEMPLO

pytestmark = pytest.mark.usefixtures("usuario")

client = TestClient(app=app)

# id: (nome, kcal e proteina por 100 g)
TACO = {1: ("Arroz", 100.0, 2.5), 2: ("Feijao", 80.0, 4.8), 3: ("Macarrao", 150.0, 10)}
PLANO = {
    "refeicoes": [
        {
            "nome": "Almoco",
            "itens": [
                {"alimento_id": 1, "gramas": 200},
                {"alimento_id": 2, "gramas": 100},
            ],
        },
        {"nome": "Jantar", "itens": [{"alimento_id": 1, "gramas": 100}]},
    ]
}
ADESAO = [{"refeicao": "Almoco", "adesao": 0.5}, {"refeicao": "Jantar", "adesao": 1}]
TROCA = {
    "refeicao": "Almoco",
    "original_id": 1,
    "substituto_id": 3,
    "motivo": "prefere macarrao",
}
FORA_DA_REFEICAO = TROCA | {"refeicao": "Jantar", "original_id": 2}  # sem feijao
ESTIMATIVA = {"adesao": ADESAO, "trocas": [TROCA]}
# ideal: 200 + 80 + 100; realista: almoco pela metade com macarrao no lugar do
# arroz (100 g x 1,5 + 50 g x 0,8) e jantar inteiro (100)
KCAL_IDEAL, KCAL_REALISTA = 380, 290
# mesma conta na proteina: 5 + 4,8 + 2,5 e 10 + 2,4 + 2,5
PROTEINA_IDEAL, PROTEINA_REALISTA = 12.3, 14.9


def busca(nome: str) -> SimpleNamespace:
    """resposta do llm pedindo a ferramenta de busca.

    Returns:
        interacao falsa com um function_call.
    """
    chamada = FunctionCallStep(
        id="c1", name="buscar_alimentos", arguments={"nome": nome}
    )
    return SimpleNamespace(steps=[chamada], output_text=None, usage=USO)


def final(saida) -> SimpleNamespace:
    """resposta final do llm, em json.

    Returns:
        interacao falsa com o texto.
    """
    texto = saida if isinstance(saida, str) else json.dumps(saida)
    return SimpleNamespace(steps=[], output_text=texto, usage=USO)


def provedor(monkeypatch, respostas):
    """troca o gemini por respostas fixas, uma por chamada.

    Returns:
        argumentos de cada chamada ao provedor.
    """
    fila, chamadas = iter(respostas), []

    def create(**kwargs):
        chamadas.append(kwargs)
        return next(fila)

    falso = SimpleNamespace(interactions=SimpleNamespace(create=create))
    monkeypatch.setattr(cliente, "_cliente", lambda: falso)
    monkeypatch.setenv("LLM_MODELO", "modelo-teste")
    return chamadas


def carregar(_db, ids):
    """TACO em memoria.

    Returns:
        id -> (nome, nutrientes por 100 g).
    """
    return {i: (TACO[i][0], {"kcal": TACO[i][1], "proteina": TACO[i][2]}) for i in ids}


@pytest.fixture
def kcal(monkeypatch):
    """troca a TACO e a projecao por versoes em memoria.

    Returns:
        kcal/dia que cada projecao recebeu, na ordem.
    """
    recebidas = []

    def projetar(*args, semanas=8):
        _, _, peso_kg, _, _, kcal_dia = args
        recebidas.append(round(kcal_dia, 6))
        # serie diferente por kcal, para ideal e realista nao se confundirem
        return [peso_kg + kcal_dia / 100 * s for s in range(semanas + 1)]

    def buscar(_db, nome):
        return [{"id": 3, "nome": "Macarrao"}] if "macarr" in nome else []

    monkeypatch.setattr(cenario, "projetar_peso", projetar)
    monkeypatch.setattr(cenario, "carregar_taco", carregar)
    monkeypatch.setattr(cenario, "buscar_taco", buscar)
    return recebidas


def nova_sessao(banco, usuario, etapa="cenarios") -> Sessao:
    """sessao do estudante com o plano encerrado.

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
        plano=PLANO,
        cenarios=None,
    )
    banco.add(sessao)
    return sessao


def post(sessao):
    """chama a rota da etapa 4.

    Returns:
        resposta http.
    """
    return client.post(f"/api/sessoes/{sessao.id}/cenarios")


def tokens(banco) -> list[ChamadaLLM]:
    """chamadas ao llm registradas.

    Returns:
        linhas de chamadas_llm no banco falso.
    """
    return [o for o in banco.objetos if isinstance(o, ChamadaLLM)]


def test_gera_uma_vez_com_a_busca_e_o_motor(monkeypatch, banco, usuario, kcal):
    """o llm busca o substituto, o motor faz as contas e a 2a chamada le o salvo."""
    chamadas = provedor(monkeypatch, [busca("macarrao"), final(ESTIMATIVA)])
    sessao = nova_sessao(banco, usuario)

    resposta = post(sessao)
    assert resposta.status_code == status.HTTP_200_OK
    corpo = resposta.json()
    ideal, realista = corpo["ideal"], corpo["realista"]
    assert kcal == [KCAL_IDEAL, KCAL_REALISTA]
    assert ideal["adequacao"]["proteina"]["consumo"] == pytest.approx(PROTEINA_IDEAL)
    assert realista["adequacao"]["proteina"]["consumo"] == pytest.approx(
        PROTEINA_REALISTA
    )
    assert ideal["peso"][1]["peso_kg"] == pytest.approx(92 + KCAL_IDEAL / 100)
    assert realista["peso"][1]["peso_kg"] == pytest.approx(92 + KCAL_REALISTA / 100)
    assert [p["semana"] for p in ideal["peso"]] == list(range(9))
    assert realista["adesao"] == ADESAO
    assert realista["substituicoes"] == [
        TROCA | {"original": "Arroz", "substituto": "Macarrao"}
    ]
    assert corpo["aviso"] == cenario.AVISO

    # o resultado da ferramenta volta ao llm ligado ao id da chamada
    assert chamadas[0]["tools"][0]["name"] == "buscar_alimentos"
    assert 0 < chamadas[0]["timeout"] <= cenario.TIMEOUT_CHAMADA
    retorno = chamadas[1]["input"][-1]
    assert retorno["type"] == "function_result"
    assert retorno["call_id"] == "c1"
    assert "Macarrao" in retorno["result"]
    assert len(tokens(banco)) == 2  # noqa: PLR2004
    assert sessao.cenarios == corpo

    # sem chamar o llm de novo: a fila de respostas ja acabou
    assert post(sessao).json() == corpo
    assert len(chamadas) == 2  # noqa: PLR2004


def test_duplo_clique_devolve_o_que_ja_foi_gravado(monkeypatch, banco, usuario, kcal):
    """outra requisicao gravou enquanto o llm respondia: vale a gravada."""
    provedor(monkeypatch, [busca("macarrao"), final(ESTIMATIVA)] * 2)
    gravado = post(nova_sessao(banco, usuario)).json() | {"aviso": "o primeiro"}
    sessao = nova_sessao(banco, usuario)

    def refresh(objeto, with_for_update=False):
        if with_for_update:  # a outra requisicao gravou antes do lock
            objeto.cenarios = gravado

    monkeypatch.setattr(banco, "refresh", refresh)
    resposta = post(sessao)
    assert resposta.json()["aviso"] == "o primeiro"
    assert sessao.cenarios is gravado


def test_saida_incoerente_tenta_de_novo(monkeypatch, banco, usuario, kcal):
    """substituto que a busca nao devolveu e inventado: pede de novo."""
    sem_busca = final(ESTIMATIVA)
    provedor(monkeypatch, [sem_busca, busca("macarrao"), final(ESTIMATIVA)])
    resposta = post(nova_sessao(banco, usuario))
    assert resposta.status_code == status.HTTP_200_OK
    assert kcal == [KCAL_IDEAL, KCAL_REALISTA]


@pytest.mark.parametrize(
    "saida",
    [
        "nao e json",
        {"adesao": ADESAO[:1], "trocas": []},  # falta o jantar
        {"adesao": ADESAO, "trocas": [FORA_DA_REFEICAO]},
        {"adesao": ADESAO, "trocas": [TROCA | {"refeicao": "Ceia"}]},
        {"adesao": ADESAO, "trocas": [TROCA, TROCA | {"motivo": "de novo"}]},
        {"adesao": [a | {"adesao": 0} for a in ADESAO], "trocas": []},
    ],
)
@pytest.mark.usefixtures("kcal")
def test_saida_invalida_em_todas_as_tentativas_da_503(
    monkeypatch, banco, usuario, saida
):
    """depois das tentativas, 503 com os tokens guardados e nada salvo."""
    respostas = [busca("macarrao"), final(saida)] * cliente.TENTATIVAS
    provedor(monkeypatch, respostas)
    sessao = nova_sessao(banco, usuario)
    resposta = post(sessao)
    assert resposta.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert resposta.json()["erro"]["codigo"] == "cenario_nao_gerado"
    registros = tokens(banco)
    assert len(registros) == cliente.TENTATIVAS * 2
    assert [r.tentativa for r in registros] == [1, 1, 2, 2, 3, 3]
    assert {(r.tokens_entrada, r.tokens_saida) for r in registros} == {
        (TOKENS, SAIDA + RACIOCINIO)
    }
    assert sessao.cenarios is None


def test_busca_sem_fim_conta_como_saida_invalida(monkeypatch, banco, usuario, kcal):
    """o llm que so busca nao trava a rota: para em BUSCAS por tentativa."""
    chamadas = provedor(monkeypatch, [busca("arroz")] * 100)
    resposta = post(nova_sessao(banco, usuario))
    assert resposta.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert len(chamadas) == cenario.BUSCAS * cliente.TENTATIVAS
    assert kcal == []


@pytest.mark.usefixtures("kcal")
def test_prazo_esgotado_da_503(monkeypatch, banco, usuario):
    """a geracao inteira tem prazo; estourou, o estudante tenta de novo."""
    chamadas = provedor(monkeypatch, [])
    monkeypatch.setattr(cenario, "PRAZO", 0)
    resposta = post(nova_sessao(banco, usuario))
    assert resposta.json()["erro"]["codigo"] == "cenario_nao_gerado"
    assert chamadas == []


@pytest.mark.usefixtures("kcal")
def test_peso_fora_da_faixa_da_503(monkeypatch, banco, usuario):
    """a projecao recusa o peso: 503 com os tokens guardados."""
    provedor(monkeypatch, [busca("macarrao"), final(ESTIMATIVA)])

    def projetar(*_args, **_kwargs):
        raise ValueError("semana 3: peso projetado fora da faixa")

    monkeypatch.setattr(cenario, "projetar_peso", projetar)
    resposta = post(nova_sessao(banco, usuario))
    assert resposta.json()["erro"]["codigo"] == "cenario_nao_gerado"
    assert len(tokens(banco)) == 2  # noqa: PLR2004


@pytest.mark.usefixtures("kcal")
def test_erro_inesperado_da_500_e_guarda_os_tokens(monkeypatch, banco, usuario):
    """alimento fora da TACO e bug: 500, mas os tokens gastos ficam."""
    provedor(monkeypatch, [busca("macarrao"), final(ESTIMATIVA)])
    sem_macarrao = lambda db, ids: carregar(db, ids - {3})  # noqa: E731
    monkeypatch.setattr(cenario, "carregar_taco", sem_macarrao)
    resposta = post(nova_sessao(banco, usuario))
    assert resposta.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert len(tokens(banco)) == 2  # noqa: PLR2004
    assert banco.commits >= 2  # noqa: PLR2004


@pytest.mark.usefixtures("kcal")
def test_gemini_fora_do_ar_da_503(monkeypatch, banco, usuario):
    """falha passageira do provedor tambem e cenario_nao_gerado."""
    provedor_com_erro(monkeypatch, InternalServerError, 503)
    resposta = post(nova_sessao(banco, usuario))
    assert resposta.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert resposta.json()["erro"]["codigo"] == "cenario_nao_gerado"


@pytest.mark.parametrize("etapa", ["anamnese", "plano"])
def test_fora_da_etapa_da_409(banco, usuario, etapa):
    """antes de encerrar o plano nao ha cenario."""
    resposta = post(nova_sessao(banco, usuario, etapa))
    assert resposta.status_code == status.HTTP_409_CONFLICT
    assert resposta.json()["erro"]["codigo"] == "etapa_invalida"


@pytest.mark.usefixtures("banco")
def test_sessao_inexistente_da_404():
    """mesmo 404 das outras rotas da sessao."""
    resposta = client.post(f"/api/sessoes/{uuid4()}/cenarios")
    assert resposta.status_code == status.HTTP_404_NOT_FOUND
