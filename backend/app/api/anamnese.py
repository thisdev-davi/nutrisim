# etapa 2: conversa com o paciente simulado (NS-020)
# a fala vai inteira num trecho so; a NS-070 quebra em varios
import html
from collections.abc import Iterable
from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.sse import EventSourceResponse, ServerSentEvent
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.auth import UsuarioAtual
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

Banco = Annotated[Session, Depends(obter_sessao)]


class Fala(BaseModel):
    """fala do paciente."""

    texto: str = Field(min_length=1)


def responder(
    db: Session,
    paciente: FichaPaciente,
    historico: list[modelos.Mensagem],
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
        tag = "resposta" if autor == "paciente" else "pergunta"
        # escapa para nenhuma fala fechar a tag e forjar outro turno
        return f"<{tag}>{html.escape(texto, quote=False)}</{tag}>"

    conversa = [marcar(m.autor, m.texto) for m in historico]
    conversa.append(marcar("estudante", pergunta))
    return gerar(
        db,
        tarefa="paciente",
        schema=Fala,
        entrada="\n".join(conversa),
        instrucao=PROMPT.read_text(encoding="utf-8")
        + paciente.model_dump_json(indent=2),
        sessao_id=sessao_id,
    ).texto


def buscar_sessao(sessao_id: str, db: Banco, usuario: UsuarioAtual) -> modelos.Sessao:
    """roda antes da rota, entao o 404 sai antes do stream abrir.

    Args:
        sessao_id: id da sessao na url.
        db: sessao do banco.
        usuario: estudante autenticado.

    Returns:
        sessao encontrada, com a ficha.

    Raises:
        ApiError: sessao inexistente ou de outro estudante.
    """
    try:
        linha = db.get(modelos.Sessao, UUID(sessao_id))
    except ValueError:
        linha = None  # id que nao e uuid tambem e 404, nao 422
    # sessao alheia tambem e 404: o 403 confirmaria que o id existe
    if linha is None or linha.usuario_id != usuario.id:
        raise ApiError(404, "sessao_nao_encontrada", "sessao nao encontrada")
    return linha


SessaoAtual = Annotated[modelos.Sessao, Depends(buscar_sessao)]


@router.get("/sessoes/{sessao_id}")
def ler_sessao(sessao: SessaoAtual) -> Sessao:
    """estado e historico, para retomar depois de recarregar a pagina.

    Args:
        sessao: sessao da url.

    Returns:
        sessao com o historico.
    """
    return para_api(sessao)


@router.post("/sessoes/{sessao_id}/mensagens", response_class=EventSourceResponse)
def enviar_mensagem(
    sessao: SessaoAtual, dados: NovaMensagem, db: Banco
) -> Iterable[ServerSentEvent]:
    """resposta do paciente em sse: "trecho", depois "fim" (ou "erro").

    Args:
        sessao: sessao da url.
        dados: pergunta do estudante.
        db: sessao do banco.

    Yields:
        eventos do stream.
    """
    paciente = FichaPaciente.model_validate(sessao.ficha["paciente"])
    # trava a sessao ate o commit: o turno seguinte espera e ve este no historico
    # ponytail: reenvio feito enquanto o llm responde ainda duplica; chave de
    # idempotencia resolve
    db.refresh(sessao, with_for_update=True)
    try:
        texto = responder(db, paciente, sessao.mensagens, dados.texto, sessao.id)
    except (SaidaInvalidaError, LLMIndisponivelError):
        db.commit()  # guarda os tokens; a pergunta nao entra, o front reenvia
        erro = Erro(
            codigo="paciente_indisponivel",
            mensagem="o paciente nao conseguiu responder, tente de novo",
        )
        yield ServerSentEvent(event="erro", data=erro)
        return
    except Exception:
        # o stream ja abriu com 200: sem o evento, o front fica sem resposta
        logger.exception("erro inesperado na sessao {}", sessao.id)
        erro = Erro(codigo="erro_interno", mensagem="erro inesperado, tente de novo")
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
