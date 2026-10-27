import json
import re
from pathlib import Path
from types import SimpleNamespace
from typing import get_args

import pytest

from app.eval import juiz
from app.llm import cliente
from app.schemas.ficha import Ficha

FICHA = Ficha.model_validate_json(
    Path(__file__).with_name("ficha_exemplo.json").read_text(encoding="utf-8")
)
CONVERSA = [
    juiz.Turno(pergunta="O que traz você aqui hoje?", resposta="A pressão."),
    juiz.Turno(pergunta="Você bebe no fim de semana?", resposta="Não bebo nada."),
]
CONTRADICAO = '{"categoria": "contradicao", "justificativa": "nega a cerveja"}'


class BancoFalso(list):
    """guarda o que seria gravado no banco."""

    add = list.append


@pytest.fixture
def chamadas(monkeypatch):
    """liga os modelos no ambiente e devolve a lista de chamadas ao gemini.

    Returns:
        lista onde cada chamada guarda os argumentos recebidos.
    """
    monkeypatch.setenv("LLM_MODELO", "modelo-paciente")
    monkeypatch.setenv("LLM_MODELO_JUIZ", "modelo-juiz")
    return []


def provedor_falso(monkeypatch, chamadas, textos):
    """troca o gemini por respostas fixas, uma por chamada."""
    respostas = iter(textos)

    def create(**kwargs):
        chamadas.append(kwargs)
        return SimpleNamespace(output_text=next(respostas), usage=None)

    falso = SimpleNamespace(interactions=SimpleNamespace(create=create))
    monkeypatch.setattr(cliente, "_cliente", lambda: falso)


def test_julga_o_ultimo_turno_com_o_modelo_do_juiz(monkeypatch, chamadas):
    """o veredito e do ultimo turno e a chamada usa LLM_MODELO_JUIZ."""
    provedor_falso(monkeypatch, chamadas, [CONTRADICAO])
    db = BancoFalso()
    veredito = juiz.julgar(db, ficha=FICHA, conversa=CONVERSA)

    assert veredito == juiz.Veredito(
        turno=2, categoria="contradicao", justificativa="nega a cerveja"
    )
    assert chamadas[0]["model"] == "modelo-juiz"
    assert db[0].tarefa == "juiz"
    entrada = json.loads(chamadas[0]["input"])
    assert entrada["turno_avaliado"]["resposta"] == "Não bebo nada."
    assert len(entrada["conversa_anterior"]) == 1
    # o juiz precisa ver o gabarito para pegar vazamento
    assert entrada["ficha"]["gabarito"]["conduta_esperada"] == "plano"


def test_categoria_fora_da_lista_tenta_de_novo(monkeypatch, chamadas):
    """categoria inventada pelo llm nao passa no schema e gera nova tentativa."""
    inventada = '{"categoria": "parcialmente_consistente", "justificativa": "x"}'
    provedor_falso(monkeypatch, chamadas, [inventada, CONTRADICAO])
    veredito = juiz.julgar(BancoFalso(), ficha=FICHA, conversa=CONVERSA)
    assert veredito.categoria == "contradicao"
    assert len(chamadas) == 2  # noqa: PLR2004


def test_saida_invalida_vira_veredito_com_falha(monkeypatch, chamadas):
    """depois das tentativas do cliente, a rodada segue com a falha marcada."""
    provedor_falso(monkeypatch, chamadas, ["nao e json"] * cliente.TENTATIVAS)
    veredito = juiz.julgar(BancoFalso(), ficha=FICHA, conversa=CONVERSA)
    assert veredito == juiz.Veredito(
        turno=2, categoria=None, justificativa=None, falha="saida_invalida"
    )


@pytest.mark.parametrize("modelo_juiz", ["", "modelo-paciente"])
def test_modelo_do_juiz_vazio_ou_igual_ao_do_paciente(
    chamadas, monkeypatch, modelo_juiz
):
    """sem modelo proprio o juiz nao chama o gemini (ADR-005)."""
    monkeypatch.setenv("LLM_MODELO_JUIZ", modelo_juiz)
    with pytest.raises(juiz.ModeloJuizError):
        juiz.julgar(BancoFalso(), ficha=FICHA, conversa=CONVERSA)
    assert chamadas == []


def test_conversa_vazia(chamadas):
    """sem resposta do paciente nao ha o que julgar."""
    with pytest.raises(ValueError, match="conversa vazia"):
        juiz.julgar(BancoFalso(), ficha=FICHA, conversa=[])


def test_prompt_versionado_cita_as_categorias_do_schema():
    """o prompt e o schema falam das mesmas cinco categorias."""
    prompt = (juiz.PASTA_PROMPTS / f"{juiz.VERSAO_PROMPT}.md").read_text(
        encoding="utf-8"
    )
    citadas = set(re.findall(r"`([a-z_]+)`", prompt))
    assert set(get_args(juiz.Categoria)) <= citadas
