import json

from app.eval import coerencia, runner
from app.llm.cliente import SaidaInvalidaError
from app.motor.precos import precos
from app.schemas.api import CenarioRealista

# hipertensao: aversao a figado, orcamento de 1100/mes e recordatorio das 6h
# as 19h30, sem nada depois das 21h
FICHA = runner.ler_fichas(
    ["adulto-hipertensao-facil-01"], runner.PASTA_EVALS / "fichas"
)[0]
ADESAO_OK = [
    {"refeicao": r.nome, "adesao": 0.9} for r in coerencia.PLANO_FIXO.refeicoes[:4]
] + [{"refeicao": "Ceia", "adesao": 0.3}]


def cenario(adesao=ADESAO_OK, substituicoes=()):
    """cenario realista so com o que as regras leem.

    Returns:
        cenario sem peso nem adequacao.
    """
    return CenarioRealista(
        peso=[], adequacao={}, adesao=adesao, substituicoes=list(substituicoes)
    )


def troca(substituto_id, substituto, original_id=402, refeicao="Almoço"):
    """troca de um item do plano fixo.

    Returns:
        substituicao no formato do cenario.
    """
    return {
        "refeicao": refeicao,
        "original_id": original_id,
        "original": "Frango",
        "substituto_id": substituto_id,
        "substituto": substituto,
        "motivo": "teste",
    }


def test_cenario_coerente_nao_viola_nada():
    """troca plausivel e adesao baixa na ceia passam."""
    c = cenario(substituicoes=[troca(352, "Carne, bovina, coxão mole")])
    assert coerencia.violacoes(FICHA.ficha, coerencia.PLANO_FIXO, c, precos()) == {}


def test_substituto_com_aversao():
    """trocar por figado contradiz a aversao da ficha."""
    c = cenario(substituicoes=[troca(999, "Fígado, bovino, grelhado")])
    v = coerencia.violacoes(FICHA.ficha, coerencia.PLANO_FIXO, c, precos())
    assert list(v) == ["substituto_com_aversao"]


def test_troca_que_estoura_o_orcamento():
    """troca cara o bastante passa do orcamento diario."""
    # 120 g de frango por um alimento de R$ 30/100 g passa dos R$ 36,67/dia
    c = cenario(substituicoes=[troca(1, "Caro")])
    v = coerencia.violacoes(FICHA.ficha, coerencia.PLANO_FIXO, c, {**precos(), 1: 30})
    assert list(v) == ["troca_estoura_orcamento"]
    # sem preco do substituto a troca nao entra na conta
    assert coerencia.violacoes(FICHA.ficha, coerencia.PLANO_FIXO, c, precos()) == {}


def test_adesao_alta_em_refeicao_que_o_paciente_nao_faz():
    """ceia seguida, mas o recordatorio acaba as 19h30."""
    adesao = [*ADESAO_OK[:4], {"refeicao": "Ceia", "adesao": 0.8}]
    v = coerencia.violacoes(
        FICHA.ficha, coerencia.PLANO_FIXO, cenario(adesao), precos()
    )
    assert list(v) == ["adesao_fora_da_rotina"]


def test_plano_fixo_tem_preco_em_tudo():
    """sem preco a regra de orcamento nao enxerga o plano."""
    ids = {i.alimento_id for r in coerencia.PLANO_FIXO.refeicoes for i in r.itens}
    assert ids <= set(precos())


def test_runner_mede_a_taxa_e_retoma(tmp_path):
    """falha fica fora da taxa e o lote retomado pula o feito."""
    respostas = iter([
        cenario(substituicoes=[troca(999, "Fígado")]),
        cenario(),
        SaidaInvalidaError("x"),
    ])

    def gerar(_ficha):
        r = next(respostas)
        if isinstance(r, Exception):
            raise r
        return r

    arquivo = tmp_path / "r.json"
    kwargs = {
        "execucoes": 3,
        "arquivo": arquivo,
        "ritmo": runner.Ritmo(0),
        "db": runner.BancoMemoria(),
    }
    resultado = runner.rodar_cenarios([FICHA], gerar, **kwargs)
    # media por execucao: 1 na primeira, 0 na segunda, a terceira falhou
    assert resultado["metricas"] == {
        "taxa_violacao_coerencia": 0.5,
        "violacoes_por_regra": {"substituto_com_aversao": 1},
        "cenarios_com_falha": 1,
    }
    assert json.loads(arquivo.read_text())["metricas"] == resultado["metricas"]
    # o que ja rodou e pulado: gerar nao e chamado de novo
    runner.rodar_cenarios([FICHA], None, **kwargs)


def test_lanche_as_19h_conta_como_lanche_da_tarde():
    """a fruta antes da academia, as 19h, e o lanche que o plano propoe."""
    paciente = FICHA.ficha.paciente.model_copy(
        update={"recordatorio": ["7h: cafe", "13h: almoco", "19h: uma fruta"]}
    )
    ficha = FICHA.ficha.model_copy(update={"paciente": paciente})
    adesao = [
        {"refeicao": r.nome, "adesao": 1.0 if r.nome == "Lanche da tarde" else 0.5}
        for r in coerencia.PLANO_FIXO.refeicoes
    ]
    v = coerencia.violacoes(ficha, coerencia.PLANO_FIXO, cenario(adesao), precos())
    assert v == {}
