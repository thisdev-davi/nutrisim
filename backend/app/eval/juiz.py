# juiz do eval (NS-032): classifica cada resposta do paciente simulado
# categorias e prioridade em evals/README.md; modelo diferente do paciente (ADR-005)
import json
import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.llm import cliente
from app.schemas.ficha import Ficha

VERSAO_PROMPT = "juiz-v3"
PASTA_PROMPTS = Path(__file__).parents[3] / "evals" / "juiz"

Categoria = Literal[
    "consistente",
    "omissao_prevista",
    "contradicao",
    "invencao_relevante",
    "quebra_de_personagem",
]


class ModeloJuizError(Exception):
    """LLM_MODELO_JUIZ vazio ou igual ao modelo do paciente."""


class Turno(BaseModel):
    """uma pergunta do estudante e a resposta do paciente."""

    pergunta: str
    resposta: str


class SaidaJuiz(BaseModel):
    """o que o llm devolve; o numero do turno fica com o codigo."""

    categoria: Categoria
    justificativa: str = Field(min_length=1)


class Veredito(BaseModel):
    """uma linha de `vereditos` no arquivo de resultado."""

    turno: int = Field(ge=1)
    categoria: Categoria | None
    justificativa: str | None
    # preenchido quando o juiz nao conseguiu julgar; o runner tira das metricas
    falha: Literal["saida_invalida"] | None = None


def modelo_do_juiz() -> str:
    """le o modelo do juiz do ambiente e confere que nao e o do paciente.

    Returns:
        nome do modelo do juiz.

    Raises:
        ModeloJuizError: variavel vazia ou igual a LLM_MODELO.
    """
    juiz = os.environ.get("LLM_MODELO_JUIZ", "").strip()
    if not juiz:
        raise ModeloJuizError("defina LLM_MODELO_JUIZ no ambiente")
    if juiz == os.environ.get("LLM_MODELO", "").strip():
        raise ModeloJuizError("LLM_MODELO_JUIZ precisa ser diferente de LLM_MODELO")
    return juiz


def julgar(db: Session, *, ficha: Ficha, conversa: list[Turno]) -> Veredito:
    """classifica a ultima resposta da conversa.

    Saida fora do schema depois das novas tentativas do cliente vira um
    veredito com `falha`, para a rodada seguir. Erro do provedor (cota, rede)
    sobe para o runner decidir a pausa.

    Args:
        db: sessao do banco onde os tokens sao registrados.
        ficha: ficha oculta completa, com restricoes e gabarito.
        conversa: turnos ate o avaliado, que e o ultimo.

    Returns:
        veredito do ultimo turno.

    Raises:
        ValueError: conversa vazia.
    """
    if not conversa:
        raise ValueError("conversa vazia: nao ha resposta para julgar")
    modelo = modelo_do_juiz()
    turno = len(conversa)
    entrada = json.dumps(
        {
            "ficha": ficha.model_dump(mode="json"),
            "conversa_anterior": [t.model_dump() for t in conversa[:-1]],
            "turno_avaliado": {"turno": turno, **conversa[-1].model_dump()},
        },
        ensure_ascii=False,
    )
    instrucao = (PASTA_PROMPTS / f"{VERSAO_PROMPT}.md").read_text(encoding="utf-8")
    try:
        saida = cliente.gerar(
            db,
            tarefa="juiz",
            schema=SaidaJuiz,
            entrada=entrada,
            instrucao=instrucao,
            modelo=modelo,
        )
    except cliente.SaidaInvalidaError:
        return Veredito(
            turno=turno, categoria=None, justificativa=None, falha="saida_invalida"
        )
    return Veredito(turno=turno, **saida.model_dump())
