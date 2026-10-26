# etapa 2: conversa com o paciente simulado (NS-020)
# a fala vai inteira num trecho so; a NS-070 quebra em varios
import html
from collections.abc import AsyncIterable
from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool
from fastapi.sse import EventSourceResponse, ServerSentEvent
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.caso import para_api
from app.api.erros import ApiError
from app.db import modelos
from app.db.deps import obter_sessao
from app.llm.cliente import LLMIndisponivelError, SaidaInvalidaError, gerar
from app.schemas.api import (
    Erro,
    Etapa,
    EtapaAtual,
    Fim,
    Mensagem,
    NovaMensagem,
    RespostaErro,
    Sessao,
    Trecho,
)
from app.schemas.ficha import FichaPaciente

router = APIRouter(
    tags=["etapa 2: anamnese"],
    responses={404: {"model": RespostaErro}, 422: {"model": RespostaErro}},
)

PROMPT = Path(__file__).parents[1] / "llm" / "prompts" / "paciente-v1.md"

# alias antes da rota obter_sessao, que sombreia a dependencia de mesmo nome
Banco = Annotated[Session, Depends(obter_sessao)]


class Fala(BaseModel):
    """fala do paciente."""

    texto: str = Field(min_length=1)


def responder(
    db: Session,
    paciente: FichaPaciente,
    historico: list[Mensagem],
    pergunta: str,
    sessao_id: UUID | None = None,
) -> str:
    """fala do paciente para a pergunta; o eval chama direto, sem a rota.

    So a parte do paciente entra no prompt: restricoes e gabarito nem chegam
    ao llm, entao nao tem como vazarem.

    Args:
        db: sessao do banco, para o registro de tokens.
        paciente: o que o paciente sabe sobre si.
        historico: falas anteriores, em ordem.
        pergunta: pergunta nova do estudante.
        sessao_id: sessao do estudante, quando houver.

    Returns:
        texto da fala.
    """

    def marcar(autor: str, texto: str) -> str:
        if autor == "paciente":
            return f"<resposta>{texto}</resposta>"
        # escapa para o estudante nao fechar a tag e falar como sistema
        return f"<pergunta>{html.escape(texto, quote=False)}</pergunta>"

    conversa = [marcar(m.autor, m.texto) for m in historico]
    conversa.append(marcar("estudante", pergunta))
    return gerar(
        db,
        tarefa="paciente",
        schema=Fala,
        entrada="\n".join(conversa),
        instrucao=PROMPT.read_text() + paciente.model_dump_json(indent=2),
        sessao_id=sessao_id,
    ).texto


def buscar_sessao(sessao_id: str, db: Banco) -> modelos.Sessao:
    """roda antes da rota, entao o 404 sai antes do stream abrir.

    Args:
        sessao_id: id da sessao na url.
        db: sessao do banco.

    Returns:
        sessao encontrada, com a ficha.

    Raises:
        ApiError: sessao inexistente.
    """
    try:
        linha = db.get(modelos.Sessao, UUID(sessao_id))
    except ValueError:
        linha = None  # id que nao e uuid tambem e 404, nao 422
    if linha is None:
        raise ApiError(404, "sessao_nao_encontrada", "sessao nao encontrada")
    return linha


SessaoAtual = Annotated[modelos.Sessao, Depends(buscar_sessao)]


@router.get("/sessoes/{sessao_id}")
async def obter_sessao(sessao: SessaoAtual) -> Sessao:
    """estado e historico, para retomar depois de recarregar a pagina.

    Args:
        sessao: sessao da url.

    Returns:
        sessao com o historico.
    """
    return para_api(sessao)


@router.post("/sessoes/{sessao_id}/mensagens", response_class=EventSourceResponse)
async def enviar_mensagem(
    sessao: SessaoAtual, dados: NovaMensagem, db: Banco
) -> AsyncIterable[ServerSentEvent]:
    """resposta do paciente em sse: "trecho", depois "fim" (ou "erro").

    Args:
        sessao: sessao da url.
        dados: pergunta do estudante.
        db: sessao do banco.

    Yields:
        eventos do stream.
    """
    paciente = FichaPaciente.model_validate(sessao.ficha["paciente"])
    historico = para_api(sessao).mensagens
    try:
        # gerar bloqueia; fora do threadpool travaria as outras requisicoes
        texto = await run_in_threadpool(
            responder, db, paciente, historico, dados.texto, sessao.id
        )
    except (SaidaInvalidaError, LLMIndisponivelError):
        db.commit()  # guarda os tokens; a pergunta nao entra, o front reenvia
        erro = Erro(
            codigo="paciente_indisponivel",
            mensagem="o paciente nao conseguiu responder, tente de novo",
        )
        yield ServerSentEvent(event="erro", data=erro)
        return
    fala = modelos.Mensagem(autor="paciente", texto=texto)
    sessao.mensagens += [modelos.Mensagem(autor="estudante", texto=dados.texto), fala]
    db.commit()
    yield ServerSentEvent(event="trecho", data=Trecho(texto=texto))
    yield ServerSentEvent(event="fim", data=Fim(mensagem_id=str(fala.id)))


@router.post("/sessoes/{sessao_id}/anamnese/encerrar")
async def encerrar_anamnese(sessao: SessaoAtual) -> EtapaAtual:
    """fecha a anamnese e libera o plano alimentar.

    Args:
        sessao: sessao da url.

    Returns:
        nova etapa da sessao.
    """
    return EtapaAtual(etapa=Etapa.PLANO)
