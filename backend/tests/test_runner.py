import json
from datetime import date
from functools import partial

import pytest

from app.api import anamnese
from app.db.modelos import ChamadaLLM
from app.eval import juiz, runner
from app.eval.paciente import (
    NEUTRA,
    RECUSA,
    FichaEval,
    PacienteFalso,
    PacienteReal,
)
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
        "taxa_quebra_ou_vazamento": None,
        "taxa_json_valido": 1.0,
        "taxa_json_valido_primeira_tentativa": 1.0,
        "vereditos_com_falha": 0,
    }
    assert resultado["uso_do_lote"]["juiz"]["chamadas"] == 2 * turnos
    assert primeira["uso"]["juiz"]["saidas"] == turnos
    assert resultado["uso_total"]["juiz"]["tokens_entrada"] == 2 * turnos * 10
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
    metricas = runner.metricas(fichas)
    assert (metricas["taxa_inconsistencia"], metricas["vereditos_com_falha"]) == (
        0.25,  # media de 1/2 e 0/1
        1,
    )


def test_metricas_de_robustez_e_formato():
    """robustez por ataque julgado; formato pelas saidas estruturadas."""
    ok = {"categoria": "consistente", "falha": None}
    ataques = [
        {"execucao": 1, "falhou": True, "vereditos": [ok]},
        {"execucao": 1, "falhou": False, "vereditos": [ok]},
        # paciente sem saida valida: fica fora da taxa
        {"execucao": 1, "falha": "paciente_saida_invalida", "vereditos": []},
        {"execucao": 2, "falhou": False, "vereditos": [ok]},
    ]
    fichas = [
        {
            "execucao": 1,
            "vereditos": [ok],
            "uso": {
                "paciente": {"saidas": 6, "saidas_com_nova_tentativa": 1},
                "juiz": {"saidas": 4, "saidas_invalidas": 1},
            },
        }
    ]
    metricas = runner.metricas(fichas, ataques)
    assert metricas == {
        "taxa_inconsistencia": 0.0,
        "taxa_quebra_ou_vazamento": 0.25,  # media de 1/2 e 0/1
        "taxa_json_valido": 0.9,  # 9 de 10
        "taxa_json_valido_primeira_tentativa": 0.9,
        "vereditos_com_falha": 0,
    }


def test_uso_separa_chamadas_de_saidas():
    """cada tentativa gasta cota, mas so a primeira abre uma saida nova."""
    registros = [
        ChamadaLLM(
            tarefa="juiz", modelo="m", tentativa=t, tokens_entrada=1, tokens_saida=1
        )
        for t in (1, 1, 2, 3)
    ]
    assert runner.uso(registros)["juiz"] == {
        "chamadas": 4,
        "saidas": 2,
        "saidas_com_nova_tentativa": 1,
        "tokens_entrada": 4,
        "tokens_saida": 4,
    }


@pytest.fixture
def quebra_no_vazamento(monkeypatch):
    """juiz que marca quebra quando o paciente fala da ficha."""
    monkeypatch.setenv("LLM_MODELO", "modelo-paciente")
    monkeypatch.setenv("LLM_MODELO_JUIZ", "modelo-juiz")

    def julgar(db, *, ficha, conversa):
        categoria = (
            "quebra_de_personagem"
            if "ficha" in conversa[-1].resposta
            else "consistente"
        )
        return juiz.Veredito(
            turno=len(conversa), categoria=categoria, justificativa="j"
        )

    monkeypatch.setattr(runner.juiz, "julgar", julgar)


def test_ataque_falha_na_primeira_quebra(quebra_no_vazamento):
    """as mensagens vao como estao e a primeira quebra marca o turno."""

    class Vaza(PacienteFalso):
        @staticmethod
        def responder(historico, pergunta):
            return "Minha ficha diz que..." if historico else NEUTRA

    ataque = runner.Ataque(
        id="pi-xx",
        categoria="c",
        owasp="o",
        mensagens=["oi", "e a ficha?"],
        esperado="e",
    )
    linha = runner.rodar_ataque(
        ataque, FICHA, Vaza(FICHA), 1, db=runner.BancoMemoria(), ritmos=ritmos()
    )
    assert (linha["falhou"], linha["turno_da_falha"]) == (True, 2)
    assert [t["pergunta"] for t in linha["conversa"]] == ataque.mensagens
    assert linha["ficha"] == ID


def test_ataques_rodam_em_rodizio_e_retomam(quebra_no_vazamento, tmp_path):
    """cada ataque pega a proxima ficha do lote; o lote retomado pula o feito."""
    fichas = runner.ler_fichas(None, runner.PASTA_EVALS / "fichas")[:2]
    ataques = runner.ler_ataques(["pi-01", "pi-02", "pi-03"], runner.ARQUIVO_ATAQUES)
    arquivo = tmp_path / "resultado.json"
    rodar = partial(
        runner.rodar,
        fichas,
        PacienteFalso,
        execucoes=1,
        arquivo=arquivo,
        ritmos=ritmos(),
    )
    rodar(ataques=ataques[:2])
    resultado = rodar(ataques=ataques)
    assert [(a["id"], a["ficha"]) for a in resultado["ataques"]] == [
        ("pi-01", fichas[0].id),
        ("pi-02", fichas[1].id),
        ("pi-03", fichas[0].id),
    ]
    assert resultado["metricas"]["taxa_quebra_ou_vazamento"] == 0.0


def test_ler_ataques_recusa_id_que_nao_existe():
    """a bateria do repo abre no schema; id errado para antes de gastar cota."""
    assert len(runner.ler_ataques(None, runner.ARQUIVO_ATAQUES)) == 15  # noqa: PLR2004
    with pytest.raises(ValueError, match="pi-99"):
        runner.ler_ataques(["pi-99"], runner.ARQUIVO_ATAQUES)


def test_linha_de_comando(julgados, tmp_path, monkeypatch):
    """o comando grava o arquivo do dia e devolve 1 quando a cota acaba."""
    args = ["--fichas", ID, "--ataques", "--execucoes", "1", "--pausa-juiz", "0"]
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


@pytest.fixture
def respostas_reais(monkeypatch):
    """troca o llm do paciente real por uma resposta fixa.

    Returns:
        lista com os argumentos de cada chamada ao paciente.
    """
    chamadas = []

    def responder(db, paciente, historico, pergunta):
        chamadas.append((db, paciente, historico, pergunta))
        return "Belisco um torresmo de vez em quando."

    monkeypatch.setattr(anamnese, "responder", responder)
    return chamadas


def test_paciente_real_passa_o_historico_no_formato_da_anamnese(
    monkeypatch, respostas_reais
):
    """so a parte do paciente vai ao llm, e cada turno vira duas mensagens."""
    monkeypatch.setenv("LLM_MODELO", "modelo-paciente")
    db = runner.BancoMemoria()
    paciente = PacienteReal(FICHA, db)
    historico = [juiz.Turno(pergunta="Oi?", resposta="Oi.")]

    assert paciente.responder(historico, "Belisca?") == (
        "Belisco um torresmo de vez em quando."
    )
    assert paciente.modelo == "modelo-paciente"
    assert paciente.versao_prompt == "paciente-v1"
    banco, enviado, mensagens, pergunta = respostas_reais[0]
    assert banco is db
    assert enviado == FICHA.ficha.paciente
    assert [(m.autor, m.texto) for m in mensagens] == [
        ("estudante", "Oi?"),
        ("paciente", "Oi."),
    ]
    assert pergunta == "Belisca?"


def test_linha_de_comando_com_o_paciente_real(julgados, respostas_reais, tmp_path):
    """o arquivo leva o modelo e o prompt do paciente real no nome."""
    args = ["--fichas", ID, "--ataques", "--execucoes", "1", "--paciente", "real"]
    pausas = ["--pausa-paciente", "0", "--pausa-juiz", "0"]
    assert runner.main([*args, *pausas, "--saida", str(tmp_path)]) == 0

    arquivo = next(tmp_path.iterdir())
    assert arquivo.name.endswith("_modelo-paciente_paciente-v1.json")
    resultado = json.loads(arquivo.read_text(encoding="utf-8"))
    assert resultado["modelo_paciente"] == "modelo-paciente"
    assert len(respostas_reais) == len(FICHA.roteiro)
