# cliente do llm (NS-018): saida estruturada validada e tokens registrados
import os
from functools import cache
from typing import TypeVar
from uuid import UUID

from google import genai
from google.genai import types

# sem alias publico no sdk 2.x para os erros da api de interactions
from google.genai._gaos.lib.compat_errors import (  # noqa: PLC2701
    APIConnectionError,
    InternalServerError,
    RateLimitError,
)
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.db.modelos import ChamadaLLM

TENTATIVAS = 3

T = TypeVar("T", bound=BaseModel)


class SaidaInvalidaError(Exception):
    """o llm nao devolveu json valido no schema depois de todas as tentativas."""


class LLMIndisponivelError(Exception):
    """o provedor falhou (sobrecarga, fora do ar, conexao); vale tentar depois."""


@cache
def _cliente() -> genai.Client:
    # le GEMINI_API_KEY do ambiente; o padrao do sdk (3 retentativas) segurava
    # o estudante ~2 min com o gemini sobrecarregado
    retentativa = types.HttpRetryOptions(attempts=1)
    return genai.Client(http_options=types.HttpOptions(retry_options=retentativa))


def gerar(  # noqa: PLR0913
    db: Session,
    *,
    tarefa: str,
    schema: type[T],
    entrada: str,
    instrucao: str,
    sessao_id: UUID | None = None,
    modelo: str | None = None,
) -> T:
    """pede ao llm uma saida no schema e valida com pydantic.

    Cada tentativa vira uma linha em chamadas_llm (o commit fica com quem chama).

    Args:
        db: sessao do banco onde os tokens sao registrados.
        tarefa: nome da tarefa (caso, adesao, retorno, rubrica).
        schema: modelo pydantic da saida.
        entrada: mensagem do usuario para o llm.
        instrucao: prompt de sistema.
        sessao_id: sessao do estudante, quando houver.
        modelo: modelo do gemini; vazio usa LLM_MODELO (o juiz do eval passa
            LLM_MODELO_JUIZ).

    Returns:
        saida validada.

    Raises:
        SaidaInvalidaError: nenhuma tentativa passou no schema.
        LLMIndisponivelError: o provedor falhou de forma passageira.
    """
    modelo = modelo or os.environ["LLM_MODELO"]
    erro: ValidationError | None = None
    for tentativa in range(1, TENTATIVAS + 1):
        try:
            resposta = _cliente().interactions.create(
                model=modelo,
                input=entrada,
                system_instruction=instrucao,
                store=False,  # nao guarda a conversa no servidor do provedor
                response_format={
                    "type": "text",
                    "mime_type": "application/json",
                    "schema": schema.model_json_schema(),
                },
            )
        # 4xx fica de fora de proposito: e bug nosso, nao sobrecarga
        except (InternalServerError, RateLimitError, APIConnectionError) as e:
            raise LLMIndisponivelError(f"{tarefa}: provedor indisponivel") from e
        uso = resposta.usage  # vem None quando a saida e bloqueada
        db.add(
            ChamadaLLM(
                sessao_id=sessao_id,
                tarefa=tarefa,
                modelo=modelo,
                tentativa=tentativa,
                tokens_entrada=getattr(uso, "total_input_tokens", None) or 0,
                # o gemini cobra o raciocinio como saida
                tokens_saida=sum(
                    getattr(uso, campo, None) or 0
                    for campo in ("total_output_tokens", "total_thought_tokens")
                ),
            )
        )
        try:
            return schema.model_validate_json(resposta.output_text or "")
        except ValidationError as e:
            erro = e
    raise SaidaInvalidaError(
        f"{tarefa}: saida invalida em {TENTATIVAS} tentativas"
    ) from erro
