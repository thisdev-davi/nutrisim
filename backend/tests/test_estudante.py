import json

import pytest

from app.eval import estudante, juiz, runner
from app.eval.estudante import EstudanteLLM, EstudanteRoteiro, SaidaEstudante
from app.eval.paciente import PacienteFalso
from app.llm.cliente import SaidaInvalidaError

ID = "adulto-hipertensao-facil-01"
FICHA = runner.ler_fichas([ID], runner.PASTA_EVALS / "fichas")[0]
HISTORICO = [juiz.Turno(pergunta="Oi, tudo bem?", resposta="Tudo, e você?")]


@pytest.fixture
def gerados(monkeypatch):
    """troca o gemini por um que devolve a pergunta do roteiro com prefixo.

    Returns:
        lista com os argumentos de cada chamada.
    """
    monkeypatch.setenv("LLM_MODELO", "modelo-paciente")
    monkeypatch.setenv("LLM_MODELO_JUIZ", "modelo-juiz")
    monkeypatch.delenv("LLM_MODELO_ESTUDANTE", raising=False)
    chamadas = []

    def gerar(db, **kwargs):
        chamadas.append(kwargs)
        entrada = json.loads(kwargs["entrada"])
        return SaidaEstudante(pergunta=f"  E aí, {entrada['pergunta_do_roteiro']} ")

    monkeypatch.setattr(estudante.cliente, "gerar", gerar)
    return chamadas


def test_estudante_roteiro_le_a_pergunta_como_esta():
    """sem llm, a pergunta sai igual ao roteiro."""
    passo = FICHA.roteiro[2]
    assert EstudanteRoteiro().perguntar(HISTORICO, passo) == passo.pergunta


def test_estudante_llm_nao_ve_o_que_o_paciente_esconde(gerados):
    """vao a conversa e a pergunta; esperado, item e ficha ficam de fora."""
    passo = FICHA.roteiro[3]  # o gatilho da omissao
    aluno = EstudanteLLM(runner.BancoMemoria())

    assert aluno.perguntar(HISTORICO, passo) == f"E aí, {passo.pergunta}"
    chamada = gerados[0]
    assert chamada["tarefa"] == "estudante"
    assert chamada["modelo"] == "modelo-juiz"  # sem LLM_MODELO_ESTUDANTE
    assert json.loads(chamada["entrada"]) == {
        "conversa_anterior": [t.model_dump() for t in HISTORICO],
        "pergunta_do_roteiro": passo.pergunta,
    }
    assert passo.item not in chamada["entrada"]
    assert aluno.versao_prompt == "estudante-v1"


def test_estudante_llm_usa_o_modelo_proprio_quando_definido(gerados, monkeypatch):
    """LLM_MODELO_ESTUDANTE vence o modelo do juiz."""
    monkeypatch.setenv("LLM_MODELO_ESTUDANTE", "modelo-estudante")
    aluno = EstudanteLLM(runner.BancoMemoria())
    aluno.perguntar([], FICHA.roteiro[0])
    assert aluno.modelo == gerados[0]["modelo"] == "modelo-estudante"


def test_estudante_llm_sem_saida_valida_le_o_roteiro(monkeypatch):
    """a entrevista segue com a pergunta original."""
    monkeypatch.setenv("LLM_MODELO_JUIZ", "modelo-juiz")

    def gerar(db, **kwargs):
        raise SaidaInvalidaError("estudante")

    monkeypatch.setattr(estudante.cliente, "gerar", gerar)
    passo = FICHA.roteiro[0]
    assert EstudanteLLM(runner.BancoMemoria()).perguntar([], passo) == passo.pergunta


class Eco(EstudanteRoteiro):
    """estudante que marca as perguntas que fez."""

    modelo, versao_prompt = "estudante-eco", "eco-v1"

    @staticmethod
    def perguntar(historico, passo):
        """pergunta do roteiro marcada.

        Returns:
            pergunta com o numero do turno.
        """
        return f"{len(historico) + 1}: {passo.pergunta}"


def test_paciente_ouve_a_pergunta_do_estudante(julgados):
    """a conversa guarda a pergunta feita e a do roteiro."""
    perguntas = []

    class Ouvinte(PacienteFalso):
        @staticmethod
        def responder(historico, pergunta):
            perguntas.append(pergunta)
            return "ok"

    linha = runner.rodar_ficha(
        FICHA,
        Ouvinte(FICHA),
        1,
        db=runner.BancoMemoria(),
        ritmos=(runner.Ritmo(0), runner.Ritmo(0)),
        estudante=Eco(),
    )
    assert perguntas[1] == f"2: {FICHA.roteiro[1].pergunta}"
    turno = linha["conversa"][1]
    assert turno["pergunta"] == perguntas[1]
    assert turno["pergunta_roteiro"] == FICHA.roteiro[1].pergunta
    assert "turnos_cortados" not in linha


def test_limite_de_turnos_corta_o_roteiro(julgados, tmp_path):
    """so as primeiras perguntas rodam, e o corte fica registrado."""
    arquivo = tmp_path / "resultado.json"
    runner.rodar(
        [FICHA],
        PacienteFalso,
        execucoes=1,
        arquivo=arquivo,
        ritmos=(runner.Ritmo(0), runner.Ritmo(0)),
        estudante=Eco(),
        max_turnos=3,
    )
    resultado = json.loads(arquivo.read_text(encoding="utf-8"))
    linha = resultado["fichas"][0]
    assert len(linha["conversa"]) == len(linha["vereditos"]) == 3  # noqa: PLR2004
    assert linha["turnos_cortados"] == len(FICHA.roteiro) - 3
    assert resultado["modelo_estudante"] == "estudante-eco"
    assert resultado["versao_prompt_estudante"] == "eco-v1"
    assert resultado["max_turnos"] == 3  # noqa: PLR2004


def test_linha_de_comando_com_o_estudante_llm(julgados, gerados, tmp_path, monkeypatch):
    """o estudante no modelo do juiz divide o ritmo do juiz."""
    recebido = {}
    rodar = runner.rodar

    def espiao(*args, **kwargs):
        recebido.update(kwargs)
        return rodar(*args, **kwargs)

    monkeypatch.setattr(runner, "rodar", espiao)
    args = ["--fichas", ID, "--execucoes", "1", "--estudante", "llm"]
    pausas = ["--pausa-juiz", "0", "--max-turnos", "2"]
    assert runner.main([*args, *pausas, "--saida", str(tmp_path)]) == 0

    assert recebido["ritmo_estudante"] is recebido["ritmos"][1]
    resultado = json.loads(next(tmp_path.iterdir()).read_text(encoding="utf-8"))
    assert resultado["modelo_estudante"] == "modelo-juiz"
    assert resultado["versao_prompt_estudante"] == "estudante-v1"
    assert len(gerados) == 2  # noqa: PLR2004
