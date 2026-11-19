from pathlib import Path

from app.motor.restricoes import verificar_restricoes
from app.schemas.api import ItemCalculado, Nutrientes, Plano, RefeicaoCalculada
from app.schemas.ficha import Ficha, Restricoes

EXEMPLO = (Path(__file__).parent / "ficha_exemplo.json").read_text()


def _ficha(peso=80, orcamento=900, **restricoes):
    """ficha do exemplo com as restricoes do teste.

    Returns:
        a ficha.
    """
    ficha = Ficha.model_validate_json(EXEMPLO)
    paciente = ficha.paciente.model_copy(
        update={"peso_kg": peso, "orcamento_mensal_reais": orcamento}
    )
    return ficha.model_copy(
        update={"paciente": paciente, "restricoes": Restricoes(**restricoes)}
    )


def _refeicao(nome, itens=(), **valores):
    """refeicao com itens (id, nome) e a composicao dada.

    Returns:
        a refeicao calculada.
    """
    return RefeicaoCalculada(
        nome=nome,
        itens=[
            ItemCalculado(alimento_id=i, gramas=100, nome=n, kcal=0) for i, n in itens
        ],
        composicao=Nutrientes(valores=valores, sem_dado={}),
    )


def _plano(*refeicoes, custo=10, **total):
    """plano com 2000 kcal e 100 g de proteina por padrao.

    Returns:
        o plano calculado.
    """
    total = {
        "kcal": 2000,
        "proteina": 100,
        "fibra_alimentar": 30,
        "sodio": 0,
        "gordura_saturada": 0,
    } | total
    return Plano(
        refeicoes=list(refeicoes) or [_refeicao("almoco")],
        total=Nutrientes(valores=total, sem_dado={}),
        get_kcal=2000,
        adequacao={},
        violacoes=[],
        custo_diario_reais=custo,
        sem_preco=[],
    )


def test_plano_que_cumpre_tudo_nao_tem_violacao():
    """todas as restricoes ligadas e nenhuma violada."""
    ficha = _ficha(
        sodio_max_mg=2000,
        fibras_min_g_por_1000kcal=14,
        gordura_saturada_max_pct_vet=10,
        proteina_g_kg_min=1.2,
        proteina_g_kg_max=1.5,
        alimentos_evitados=["doces"],
    )
    plano = _plano(sodio=1500, gordura_saturada=15, custo=29)
    assert verificar_restricoes(ficha, plano) == []


def test_sodio_acima_aponta_a_refeicao_com_mais_sodio():
    """o total passa do limite e a refeicao com mais sodio e marcada."""
    plano = _plano(
        _refeicao("cafe", sodio=300), _refeicao("almoco", sodio=1900), sodio=2200
    )
    [v] = verificar_restricoes(_ficha(sodio_max_mg=2000), plano)
    assert (v.tipo, v.refeicao, v.alimento_id) == ("sodio", "almoco", None)


def test_fibras_abaixo_por_1000_kcal():
    """fibra e conferida pela densidade, nao pelo total."""
    # 20 g em 2000 kcal = 10 g/1000 kcal
    ficha = _ficha(fibras_min_g_por_1000kcal=14)
    [v] = verificar_restricoes(ficha, _plano(fibra_alimentar=20))
    assert (v.tipo, v.refeicao) == ("fibras", None)
    assert verificar_restricoes(ficha, _plano(fibra_alimentar=28)) == []


def test_gordura_saturada_no_limite_ja_viola():
    """o limite e menos de 10% do VET."""
    # 20 g x 9 / 1800 kcal = 10%: o limite e menos de 10%
    plano = _plano(
        _refeicao("jantar", gordura_saturada=20), gordura_saturada=20, kcal=1800
    )
    [v] = verificar_restricoes(_ficha(gordura_saturada_max_pct_vet=10), plano)
    assert (v.tipo, v.refeicao) == ("gordura_saturada", "jantar")


def test_proteina_por_kg_abaixo_e_acima():
    """proteina usa o peso da ficha."""
    ficha = _ficha(peso=80, proteina_g_kg_min=1.2, proteina_g_kg_max=1.5)
    [abaixo] = verificar_restricoes(ficha, _plano(proteina=80))  # 1,0 g/kg
    assert (abaixo.tipo, abaixo.refeicao) == ("proteina", None)
    plano = _plano(_refeicao("almoco", proteina=90), proteina=130)  # 1,6 g/kg
    [acima] = verificar_restricoes(ficha, plano)
    assert (acima.tipo, acima.refeicao) == ("proteina", "almoco")


def test_alimento_evitado_aponta_refeicao_e_item():
    """cada item evitado vira uma violacao com refeicao e id."""
    plano = _plano(
        _refeicao("lanche", [(1, "Pão, trigo, francês"), (2, "Doce, de leite")]),
        _refeicao("ceia", [(3, "Bebida láctea, pêssego")]),
    )
    ficha = _ficha(alimentos_evitados=["doces", "bebidas adoçadas"])
    violacoes = verificar_restricoes(ficha, plano)
    assert [(v.tipo, v.refeicao, v.alimento_id) for v in violacoes] == [
        ("alimento_evitado", "lanche", 2),
        ("alimento_evitado", "ceia", 3),
    ]


def test_orcamento_diario_e_o_mensal_por_30():
    """o orcamento do dia e o mensal dividido por 30."""
    ficha = _ficha(orcamento=900)  # R$ 30/dia
    assert verificar_restricoes(ficha, _plano(custo=30)) == []
    [v] = verificar_restricoes(ficha, _plano(custo=30.5))
    assert (v.tipo, v.refeicao, v.alimento_id) == ("orcamento", None, None)
