# etapa 4: cenarios ideal e realista (NS-046)
from fastapi import APIRouter
from loguru import logger

from app.api.anamnese import Banco, SessaoAtual
from app.api.erros import ApiError
from app.llm.cenario import gerar_cenarios
from app.llm.cliente import LLMIndisponivelError, SaidaInvalidaError
from app.schemas.api import Cenarios, Etapa, RespostaErro

router = APIRouter(
    tags=["etapa 4: cenarios"],
    responses={
        404: {"model": RespostaErro},
        409: {"model": RespostaErro},
        503: {"model": RespostaErro},
    },
)


# def e nao async: o llm bloqueia, entao roda no threadpool
@router.post("/sessoes/{sessao_id}/cenarios")
def gerar(sessao: SessaoAtual, db: Banco) -> Cenarios:
    """gera os cenarios na primeira chamada; nas seguintes devolve os salvos.

    Args:
        sessao: sessao da url.
        db: sessao do banco.

    Returns:
        cenarios ideal e realista, com o aviso da projecao.

    Raises:
        ApiError: fora da etapa de cenarios, o llm falhou ou a projecao saiu
            da faixa.
    """
    if sessao.etapa != Etapa.CENARIOS:
        raise ApiError(409, "etapa_invalida", "a sessao nao esta na etapa de cenarios")
    if sessao.cenarios is not None:
        return Cenarios.model_validate(sessao.cenarios)
    db.commit()  # fecha a leitura: nada fica travado enquanto o llm responde
    try:
        cenarios = gerar_cenarios(db, sessao)
    except Exception as e:
        db.commit()  # guarda os tokens gastos, ate num erro inesperado
        logger.exception("cenario nao gerado na sessao {}", sessao.id)
        # ValueError: peso projetado fora das faixas do motor
        if isinstance(e, SaidaInvalidaError | LLMIndisponivelError | ValueError):
            raise ApiError(
                503,
                "cenario_nao_gerado",
                "nao foi possivel gerar o cenario, tente de novo",
            ) from e
        raise
    # ponytail: duplo clique gasta tokens duas vezes; o lock so garante que a
    # resposta e uma so
    db.refresh(sessao, with_for_update=True)
    if sessao.cenarios is None:
        sessao.cenarios = cenarios.model_dump(mode="json")
    db.commit()
    return Cenarios.model_validate(sessao.cenarios)
