# etapa 3: plano alimentar (NS-041) e encaminhamento (NS-071)
# o front manda so ids e gramas; todo numero da resposta sai do motor
from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.api.anamnese import Banco, SessaoAtual
from app.api.erros import ApiError
from app.db import modelos
from app.llm.cenario import carregar_taco
from app.motor.adequacao import calcular_adequacao
from app.motor.composicao import Item, calcular_composicao, calcular_refeicao
from app.motor.energia import get
from app.motor.precos import precos
from app.schemas.api import (
    AdequacaoNutriente,
    Etapa,
    EtapaAtual,
    ItemCalculado,
    NovoEncaminhamento,
    NovoPlano,
    Nutrientes,
    Plano,
    RefeicaoCalculada,
    RespostaErro,
    Violacao,
)
from app.schemas.ficha import Ficha

router = APIRouter(
    tags=["etapa 3: plano"],
    responses={
        404: {"model": RespostaErro},
        409: {"model": RespostaErro},
        422: {"model": RespostaErro},
    },
)


# trocar por app.motor.restricoes quando a NS-044 entrar
def verificar_restricoes(ficha: Ficha, plano: Plano) -> list[Violacao]:  # noqa: ARG001
    """stub da NS-044: sem violacoes ate o motor de restricoes entrar.

    Returns:
        lista vazia.
    """
    return []


def calcular(db: Session, ficha: Ficha, novo: NovoPlano) -> Plano:
    """plano com composicao, adequacao, get, custo e violacoes, tudo pelo motor.

    Args:
        db: sessao do banco, para ler a TACO.
        ficha: ficha do caso.
        novo: plano como o estudante montou.

    Returns:
        plano calculado.

    Raises:
        ApiError: algum alimento_id fora da TACO.
    """
    ids = {i.alimento_id for r in novo.refeicoes for i in r.itens}
    taco = carregar_taco(db, ids)
    if ids - taco.keys():
        raise ApiError(422, "alimento_invalido", "alimento fora da tabela TACO")
    itens = {
        r.nome: [
            Item(taco[i.alimento_id][0], i.gramas, taco[i.alimento_id][1])
            for i in r.itens
        ]
        for r in novo.refeicoes
    }
    composicao = calcular_composicao(itens)
    refeicoes = [
        RefeicaoCalculada(
            nome=r.nome,
            itens=[
                ItemCalculado(
                    **i.model_dump(),
                    nome=item.nome,
                    kcal=calcular_refeicao([item]).valores["kcal"],
                )
                for i, item in zip(r.itens, itens[r.nome], strict=True)
            ],
            composicao=Nutrientes(**vars(composicao.por_refeicao[r.nome])),
        )
        for r in novo.refeicoes
    ]
    p = ficha.paciente
    # ponytail: mesma conversao de _cenario em llm/cenario.py; extrair quando
    # cenario.py puder mudar
    adequacao = {
        n: AdequacaoNutriente(
            consumo=a.consumo,
            referencia=a.referencia.valor,
            percentual=a.percentual,
            classificacao=a.classificacao,
            sem_dado=a.sem_dado,
        )
        for n, a in calcular_adequacao(composicao.total, p.genero, p.idade).items()
    }
    tabela = precos()
    todos = [(i.alimento_id, i.gramas) for r in novo.refeicoes for i in r.itens]
    sem_preco = list(dict.fromkeys(taco[a][0] for a, _ in todos if a not in tabela))
    plano = Plano(
        refeicoes=refeicoes,
        total=Nutrientes(**vars(composicao.total)),
        get_kcal=get(p.genero, p.idade, p.peso_kg, p.altura_cm, p.atividade_fisica),
        adequacao=adequacao,
        violacoes=[],
        custo_diario_reais=sum(tabela[a] * g / 100 for a, g in todos if a in tabela),
        sem_preco=sem_preco,
    )
    plano.violacoes = verificar_restricoes(ficha, plano)
    return plano


def _exigir_etapa_plano(sessao: modelos.Sessao) -> None:
    if sessao.etapa != Etapa.PLANO:
        raise ApiError(409, "etapa_invalida", "a sessao nao esta na etapa do plano")


@router.get("/sessoes/{sessao_id}/plano")
def ler_plano(sessao: SessaoAtual, db: Banco) -> Plano:
    """plano salvo, recalculado pelo motor.

    Args:
        sessao: sessao da url.
        db: sessao do banco.

    Returns:
        plano calculado.

    Raises:
        ApiError: nenhum plano salvo ainda.
    """
    if sessao.plano is None:
        raise ApiError(404, "plano_nao_encontrado", "nenhum plano salvo")
    ficha = Ficha.model_validate(sessao.ficha)
    return calcular(db, ficha, NovoPlano.model_validate(sessao.plano))


@router.put("/sessoes/{sessao_id}/plano")
def salvar_plano(sessao: SessaoAtual, dados: NovoPlano, db: Banco) -> Plano:
    """salva o plano inteiro e devolve os numeros do motor.

    Args:
        sessao: sessao da url.
        dados: plano como o estudante montou.
        db: sessao do banco.

    Returns:
        plano calculado.
    """
    _exigir_etapa_plano(sessao)
    plano = calcular(
        db, Ficha.model_validate(sessao.ficha), dados
    )  # 422 antes de gravar
    sessao.plano = dados.model_dump(mode="json")
    db.commit()
    return plano


@router.post("/sessoes/{sessao_id}/plano/encerrar")
def encerrar_plano(sessao: SessaoAtual, db: Banco) -> EtapaAtual:
    """trava o plano e libera os cenarios.

    Args:
        sessao: sessao da url.
        db: sessao do banco.

    Returns:
        nova etapa da sessao.

    Raises:
        ApiError: fora da etapa do plano ou sem plano salvo.
    """
    _exigir_etapa_plano(sessao)
    if sessao.plano is None:
        raise ApiError(404, "plano_nao_encontrado", "nenhum plano salvo")
    sessao.etapa = Etapa.CENARIOS
    db.commit()
    return EtapaAtual(etapa=Etapa.CENARIOS)


@router.post("/sessoes/{sessao_id}/plano/encaminhar")
def encaminhar(sessao: SessaoAtual, dados: NovoEncaminhamento, db: Banco) -> EtapaAtual:
    """encaminha o paciente no lugar do plano e pula os cenarios (NS-071).

    Args:
        sessao: sessao da url.
        dados: motivo do encaminhamento.
        db: sessao do banco.

    Returns:
        nova etapa da sessao.
    """
    _exigir_etapa_plano(sessao)
    sessao.encaminhamento = dados.motivo
    sessao.etapa = Etapa.RETORNO
    db.commit()
    return EtapaAtual(etapa=Etapa.RETORNO)
