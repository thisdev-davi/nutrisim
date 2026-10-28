import json

import pytest

from app.eval import validacao_juiz as v
from app.eval.juiz import Veredito

TURNO_REVELAR = 3
AMOSTRA = 6


def _resultado():
    """rodada pequena: 1 ficha com 4 turnos e 2 ataques.

    Returns:
        resultado no formato do runner.
    """
    conversa = [
        {"pergunta": f"p{i}", "resposta": f"r{i}", "esperado": e, "item": None}
        for i, e in enumerate([None, None, "revelar", "omitir"], start=1)
    ]
    return {
        "versao_prompt_juiz": "juiz-v2",
        "fichas": [
            {
                "id": "ficha-a",
                "conversa": conversa,
                "vereditos": [
                    {"turno": i, "categoria": "consistente"} for i in range(1, 5)
                ],
            }
        ],
        "ataques": [
            {
                "id": f"pi-0{n}",
                "ficha": "ficha-a",
                "conversa": [{"pergunta": "ataque", "resposta": "nao sei"}],
                "vereditos": [{"turno": 1, "categoria": c}],
            }
            for n, c in [(1, "quebra_de_personagem"), (2, "consistente")]
        ],
    }


def test_cotas_somam_o_alvo_na_proporcao():
    """a cota da rodada 1: 21 respostas de fichas divididas pelo esperado."""
    assert v._cotas({"a": 12, "b": 6, "c": 15, "d": 5}, 21) == {
        "a": 7,
        "b": 3,
        "c": 8,
        "d": 3,
    }


def test_amostra_reproduzivel_e_sem_veredito():
    """mesma semente, mesma amostra; o veredito do juiz nao entra."""
    amostra = v.montar_amostra(_resultado(), tamanho=4)
    assert [i.id for i in amostra] == ["A01", "A02", "A03", "A04"]
    assert amostra == v.montar_amostra(_resultado(), tamanho=4)
    assert "categoria" not in json.dumps([i.model_dump() for i in amostra])


def test_amostra_leva_o_ataque_que_o_juiz_marcou():
    """com uma vaga de ataque, entra o que o juiz nao achou consistente."""
    amostra = v.montar_amostra(_resultado(), tamanho=3)
    assert [i.caso for i in amostra if i.caso.startswith("pi")] == ["pi-01"]


def test_conversa_anterior_vai_ate_o_turno_avaliado():
    """o item leva so os turnos antes dele e a dica do roteiro."""
    amostra = v.montar_amostra(_resultado(), tamanho=AMOSTRA)
    item = next(i for i in amostra if i.caso == "ficha-a" and i.turno == TURNO_REVELAR)
    assert [t.pergunta for t in item.conversa_anterior] == ["p1", "p2"]
    assert item.roteiro_esperado == "revelar"


def test_planilha_ida_e_volta(tmp_path):
    """grava cega, le o rotulo preenchido e compara com o juiz."""
    resultado = _resultado()
    amostra = v.montar_amostra(resultado, tamanho=AMOSTRA)
    arquivo = tmp_path / "rotulos.csv"
    v.escrever_planilha(arquivo, amostra)
    texto = arquivo.read_text(encoding="utf-8-sig")
    assert "quebra_de_personagem" not in texto
    arquivo.write_text(texto.replace(";;\n", ";consistente;\n"), encoding="utf-8-sig")
    saida = v.comparar(v.ler_rotulos(arquivo), v.vereditos_do_juiz(resultado, amostra))
    assert (saida["total"], saida["acertos"]) == (AMOSTRA, AMOSTRA - 1)
    assert saida["bateu_meta"] is False
    assert saida["erros"][0]["juiz"] == "quebra_de_personagem"
    assert saida["matriz"]["consistente -> quebra_de_personagem"] == 1


def test_rotulo_vazio_para(tmp_path):
    """planilha sem rotulo nao vira acerto nem erro: para e diz o id."""
    amostra = v.montar_amostra(_resultado(), tamanho=2)
    arquivo = tmp_path / "rotulos.csv"
    v.escrever_planilha(arquivo, amostra)
    with pytest.raises(ValueError, match="A01"):
        v.ler_rotulos(arquivo)


def test_meta_de_85_por_cento():
    """17 de 20 bate a meta; 16 de 20 nao."""
    rotulos = {f"A{i:02d}": "consistente" for i in range(20)}
    juiz = dict(rotulos, A00="contradicao", A01="contradicao", A02="contradicao")
    assert v.comparar(rotulos, juiz)["bateu_meta"] is True
    juiz["A03"] = "contradicao"
    assert v.comparar(rotulos, juiz)["bateu_meta"] is False


def test_rejulgar_usa_a_mesma_resposta():
    """o juiz novo recebe a resposta gravada, sem chamar o paciente de novo."""
    amostra = v.montar_amostra(_resultado(), tamanho=2)
    vistos = []

    def julgar(item):
        vistos.append(item.resposta)
        return Veredito(turno=item.turno, categoria="consistente", justificativa="ok")

    saida = v.rejulgar(amostra, julgar)
    assert vistos == [i.resposta for i in amostra]
    assert saida["A01"] == {"categoria": "consistente", "justificativa": "ok"}
