import json
from datetime import date

import pytest

from app.db.modelos import ChamadaLLM
from app.eval import juiz, runner
from app.eval.paciente import NEUTRA, RECUSA, FichaEval, PacienteFalso
from app.llm.cliente import LLMIndisponivelError, SaidaInvalidaError

ID = "adulto-hipertensao-facil-01"
FICHA = runner.ler_fichas([ID], runner.PASTA_EVALS / "fichas")[0]


class Relogio:
    """relogio que so anda quando alguem dorme."""

    def __init__(self):
        """comeca no zero."""
        self.agora, self.sonos = 0.0, []

    def dormir(self, segundos):
        """avanca o relogio."""
        self.sonos.append(segundos)
        self.agora += segundos

    def __call__(self):
        """hora atual.

        Returns:
            segundos desde o inicio.
        """
        return self.agora


def ritmos():
    """ritmos sem pausa, para os testes nao dormirem.

    Returns:
        ritmo do paciente e do juiz.
    """
    return runner.Ritmo(0), runner.Ritmo(0)


@pytest.fixture
def julgados(monkeypatch):
    """troca o juiz por um que acha contradicao so no turno 2.

    Returns:
        lista com o tamanho da conversa em cada julgamento.
    """
    monkeypatch.setenv("LLM_MODELO", "modelo-paciente")
    monkeypatch.setenv("LLM_MODELO_JUIZ", "modelo-juiz")
    chamadas = []

    def julgar(db, *, ficha, conversa):
        chamadas.append(len(conversa))
        uso = {"tokens_entrada": 10, "tokens_saida": 2}
        db.add(ChamadaLLM(tarefa="juiz", modelo="m", tentativa=1, **uso))
        categoria = "contradicao" if len(conversa) == 2 else "consistente"  # noqa: PLR2004
        return juiz.Veredito(
            turno=len(conversa), categoria=categoria, justificativa="j"
        )

    monkeypatch.setattr(runner.juiz, "julgar", julgar)
    return chamadas


def test_paciente_falso_segue_o_roteiro():
    """revela no gatilho, recusa quando deve e fica neutro no resto."""
    paciente = PacienteFalso(FICHA)
    for passo in FICHA.roteiro:
        resposta = paciente.responder([], passo.pergunta)
        if passo.esperado == "revelar":
            assert passo.item in resposta
        elif passo.esperado == "recusar":
            assert resposta == RECUSA
        else:
            assert resposta == NEUTRA
    assert paciente.responder([], "pergunta fora do roteiro") == NEUTRA


def test_ritmo_espera_so_o_que_falta():
    """a primeira chamada nao espera; a seguinte completa o intervalo."""
    relogio = Relogio()
    ritmo = runner.Ritmo(15, dormir=relogio.dormir, relogio=relogio)
    ritmo.esperar()
    relogio.agora += 5  # a chamada levou 5 s
    ritmo.esperar()
    assert relogio.sonos == [10]


def test_tenta_de_novo_quando_a_cota_estoura():
    """erro do provedor espera e repete; depois de todas as esperas, desiste."""
    relogio = Relogio()
    ritmo = runner.Ritmo(0, dormir=relogio.dormir, relogio=relogio)
    falhas = iter([LLMIndisponivelError("cota"), "ok"])

    def acao():
        item = next(falhas)
        if isinstance(item, Exception):
            raise item
        return item

    assert runner.com_ritmo(acao, ritmo, (30, 60)) == "ok"
    assert relogio.sonos == [30]

    def sempre_falha():
        raise LLMIndisponivelError("cota")

    with pytest.raises(runner.CotaEsgotadaError):
        runner.com_ritmo(sempre_falha, ritmo, (30, 60))


def test_roda_uma_ficha_de_ponta_a_ponta(julgados, tmp_path):
    """grava conversa, vereditos, modelos, versoes e metricas."""
    arquivo = runner.caminho_resultado(
        tmp_path, date(2026, 10, 27), PacienteFalso.modelo, PacienteFalso.versao_prompt
    )
    runner.rodar([FICHA], PacienteFalso, execucoes=2, arquivo=arquivo, ritmos=ritmos())

    assert arquivo.name == "2026-10-27_paciente-falso_respostas-fixas-v1.json"
    resultado = json.loads(arquivo.read_text(encoding="utf-8"))
    turnos = len(FICHA.roteiro)
    assert resultado["data"] == "2026-10-27"
    assert resultado["modelo_paciente"] == "paciente-falso"
    assert resultado["modelo_juiz"] == "modelo-juiz"
    assert resultado["versao_prompt"] == "respostas-fixas-v1"
    assert resultado["versao_prompt_juiz"] == juiz.VERSAO_PROMPT
    assert [(f["id"], f["execucao"]) for f in resultado["fichas"]] == [(ID, 1), (ID, 2)]
    primeira = resultado["fichas"][0]
    assert len(primeira["conversa"]) == len(primeira["vereditos"]) == turnos
    assert primeira["conversa"][0]["pergunta"] == FICHA.roteiro[0].pergunta
    assert resultado["metricas"] == {
        "taxa_inconsistencia": round(1 / turnos, 4),
        "vereditos_com_falha": 0,
    }
    assert resultado["uso_do_lote"]["juiz"]["chamadas"] == 2 * turnos
    assert julgados == list(range(1, turnos + 1)) * 2


def test_lote_retomado_pula_o_que_ja_rodou(julgados, tmp_path):
    """rodar de novo no mesmo arquivo so faz as execucoes que faltam."""
    arquivo = tmp_path / "resultado.json"
    runner.rodar([FICHA], PacienteFalso, execucoes=1, arquivo=arquivo, ritmos=ritmos())
    julgados.clear()
    runner.rodar([FICHA], PacienteFalso, execucoes=2, arquivo=arquivo, ritmos=ritmos())

    resultado = json.loads(arquivo.read_text(encoding="utf-8"))
    assert [f["execucao"] for f in resultado["fichas"]] == [1, 2]
    assert len(julgados) == len(FICHA.roteiro)  # so a execucao 2


def test_paciente_sem_saida_valida_encerra_a_execucao(julgados):
    """sem resposta do paciente a execucao para e fica marcada."""

    class Quebrado(PacienteFalso):
        def responder(self, historico, pergunta):
            if historico:
                raise SaidaInvalidaError("paciente")
            return super().responder(historico, pergunta)

    linha = runner.rodar_ficha(
        FICHA, Quebrado(FICHA), 1, db=runner.BancoMemoria(), ritmos=ritmos()
    )
    assert linha["falha"] == "paciente_saida_invalida"
    assert len(linha["conversa"]) == len(linha["vereditos"]) == 1


def test_metricas_ignoram_vereditos_com_falha():
    """falha do juiz sai da taxa e entra na contagem."""
    fichas = [
        {
            "execucao": 1,
            "vereditos": [
                {"categoria": "contradicao", "falha": None},
                {"categoria": "consistente", "falha": None},
                {"categoria": None, "falha": "saida_invalida"},
            ],
        },
        {"execucao": 2, "vereditos": [{"categoria": "consistente", "falha": None}]},
    ]
    assert runner.metricas(fichas) == {
        "taxa_inconsistencia": 0.25,  # media de 1/2 e 0/1
        "vereditos_com_falha": 1,
    }


def test_linha_de_comando(julgados, tmp_path, monkeypatch):
    """o comando grava o arquivo do dia e devolve 1 quando a cota acaba."""
    args = ["--fichas", ID, "--execucoes", "1", "--pausa-juiz", "0"]
    assert runner.main([*args, "--saida", str(tmp_path)]) == 0
    assert [p.name[11:] for p in tmp_path.iterdir()] == [
        "paciente-falso_respostas-fixas-v1.json"
    ]

    def sem_cota(*_, **__):
        raise runner.CotaEsgotadaError("cota")

    monkeypatch.setattr(runner, "rodar", sem_cota)
    assert runner.main([*args, "--saida", str(tmp_path)]) == 1


def test_fichas_do_repo_passam_no_schema_do_runner():
    """todas as fichas de evals/fichas abrem como FichaEval."""
    fichas = runner.ler_fichas(None, runner.PASTA_EVALS / "fichas")
    assert fichas
    assert all(isinstance(f, FichaEval) for f in fichas)
