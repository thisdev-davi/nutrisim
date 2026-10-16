from types import SimpleNamespace

import pytest
from pydantic import BaseModel

from app.llm import cliente

TOKENS = 10


class Saida(BaseModel):
    """schema de teste."""

    nota: int


class BancoFalso(list):
    """guarda o que seria gravado no banco."""

    add = list.append


def provedor_falso(monkeypatch, textos):
    """troca o gemini por respostas fixas, uma por chamada."""
    respostas = iter(textos)

    def create(**_):
        uso = SimpleNamespace(total_input_tokens=TOKENS, total_output_tokens=3)
        return SimpleNamespace(output_text=next(respostas), usage=uso)

    falso = SimpleNamespace(interactions=SimpleNamespace(create=create))
    monkeypatch.setattr(cliente, "_cliente", lambda: falso)
    monkeypatch.setenv("LLM_MODELO", "modelo-teste")


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


def test_erro_claro_quando_as_tentativas_acabam(monkeypatch):
    """depois de TENTATIVAS saidas invalidas, gera SaidaInvalidaError."""
    provedor_falso(monkeypatch, ["nao e json"] * cliente.TENTATIVAS)
    db = BancoFalso()
    with pytest.raises(cliente.SaidaInvalidaError, match="caso"):
        gerar(db)
    assert len(db) == cliente.TENTATIVAS
