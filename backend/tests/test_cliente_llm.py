from types import SimpleNamespace

import pytest
from pydantic import BaseModel

from app.llm import cliente

TOKENS = 10
SAIDA, RACIOCINIO = 3, 2


class Saida(BaseModel):
    """schema de teste."""

    nota: int


class BancoFalso(list):
    """guarda o que seria gravado no banco."""

    add = list.append


USO = SimpleNamespace(
    total_input_tokens=TOKENS,
    total_output_tokens=SAIDA,
    total_thought_tokens=RACIOCINIO,
)


def provedor_falso(monkeypatch, textos, uso=USO):
    """troca o gemini por respostas fixas, uma por chamada.

    Returns:
        argumentos de cada chamada ao provedor.
    """
    respostas = iter(textos)
    chamadas = []

    def create(**kwargs):
        chamadas.append(kwargs)
        return SimpleNamespace(output_text=next(respostas), usage=uso)

    falso = SimpleNamespace(interactions=SimpleNamespace(create=create))
    monkeypatch.setattr(cliente, "_cliente", lambda: falso)
    monkeypatch.setenv("LLM_MODELO", "modelo-teste")
    return chamadas


def gerar(db):
    """chama o cliente com valores fixos.

    Returns:
        saida validada.
    """
    return cliente.gerar(db, tarefa="caso", schema=Saida, entrada="e", instrucao="i")


def test_tenta_de_novo_e_registra_cada_tentativa(monkeypatch):
    """saida invalida gera nova tentativa; as duas chamadas ficam registradas."""
    provedor_falso(monkeypatch, ['{"nota": "dez"}', '{"nota": 10}'])
    db = BancoFalso()
    assert gerar(db) == Saida(nota=10)
    assert [c.tentativa for c in db] == [1, 2]
    assert db[0].modelo == "modelo-teste"
    assert db[0].tokens_entrada == TOKENS
    assert db[0].tokens_saida == SAIDA + RACIOCINIO  # raciocinio e cobrado como saida


def test_resposta_sem_usage_registra_zero(monkeypatch):
    """saida bloqueada vem sem usage; registra zero em vez de quebrar."""
    provedor_falso(monkeypatch, ['{"nota": 10}'], uso=None)
    db = BancoFalso()
    assert gerar(db) == Saida(nota=10)
    assert (db[0].tokens_entrada, db[0].tokens_saida) == (0, 0)


def test_erro_claro_quando_as_tentativas_acabam(monkeypatch):
    """depois de TENTATIVAS saidas invalidas, gera SaidaInvalidaError."""
    provedor_falso(monkeypatch, ["nao e json"] * cliente.TENTATIVAS)
    db = BancoFalso()
    with pytest.raises(cliente.SaidaInvalidaError, match="caso"):
        gerar(db)
    assert len(db) == cliente.TENTATIVAS


def test_modelo_da_chamada_vence_o_padrao(monkeypatch):
    """o juiz do eval passa o proprio modelo, que vai ao provedor e ao registro."""
    chamadas = provedor_falso(monkeypatch, ['{"nota": 10}'])
    db = BancoFalso()
    cliente.gerar(
        db, tarefa="juiz", schema=Saida, entrada="e", instrucao="i", modelo="juiz"
    )
    assert chamadas[0]["model"] == db[0].modelo == "juiz"
