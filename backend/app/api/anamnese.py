# etapa 2: conversa com o paciente
# mock: resposta fixa ate a NS-020 e a NS-070 ligarem o llm
import asyncio
from collections.abc import AsyncIterable
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.sse import EventSourceResponse, ServerSentEvent

from app.api.caso import SESSAO_MOCK
from app.api.erros import ApiError
from app.schemas.api import (
    Etapa,
    EtapaAtual,
    Fim,
    NovaMensagem,
    RespostaErro,
    Sessao,
    Trecho,
)

router = APIRouter(
    tags=["etapa 2: anamnese"],
    responses={404: {"model": RespostaErro}, 422: {"model": RespostaErro}},
)

FALA_MOCK = "Olha, eu como pao com manteiga todo dia de manha e quase nao bebo agua."


def buscar_sessao(sessao_id: str) -> Sessao:
    """roda antes da rota, entao o 404 sai antes do stream abrir.

    Args:
        sessao_id: id da sessao na url.

    Returns:
        sessao encontrada.

    Raises:
        ApiError: sessao inexistente.
    """
    if sessao_id != SESSAO_MOCK.id:
        raise ApiError(404, "sessao_nao_encontrada", "sessao nao encontrada")
    return SESSAO_MOCK


SessaoAtual = Annotated[Sessao, Depends(buscar_sessao)]


@router.get("/sessoes/{sessao_id}")
async def obter_sessao(sessao: SessaoAtual) -> Sessao:
    """estado e historico, para retomar depois de recarregar a pagina.

    Args:
        sessao: sessao da url.

    Returns:
        sessao com o historico.
    """
    return sessao


@router.post("/sessoes/{sessao_id}/mensagens", response_class=EventSourceResponse)
async def enviar_mensagem(
    sessao: SessaoAtual, dados: NovaMensagem
) -> AsyncIterable[ServerSentEvent]:
    """resposta do paciente em sse: varios "trecho", depois "fim" (ou "erro").

    Args:
        sessao: sessao da url.
        dados: pergunta do estudante.

    Yields:
        eventos do stream.
    """
    for palavra in FALA_MOCK.split(" "):
        await asyncio.sleep(0.05)  # simula o paciente digitando
        yield ServerSentEvent(event="trecho", data=Trecho(texto=palavra + " "))
    yield ServerSentEvent(event="fim", data=Fim(mensagem_id="m1"))


@router.post("/sessoes/{sessao_id}/anamnese/encerrar")
async def encerrar_anamnese(sessao: SessaoAtual) -> EtapaAtual:
    """fecha a anamnese e libera o plano alimentar.

    Args:
        sessao: sessao da url.

    Returns:
        nova etapa da sessao.
    """
    return EtapaAtual(etapa=Etapa.PLANO)
