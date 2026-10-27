# estudante simulado do eval (NS-031): faz ao paciente as perguntas do roteiro
# o do llm reformula cada pergunta com o contexto da conversa, sem mudar o tema
import json
import os
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.eval.juiz import Turno
from app.eval.paciente import Passo
from app.llm import cliente

VERSAO_PROMPT = "estudante-v1"
PASTA_PROMPTS = Path(__file__).parents[3] / "evals" / "estudante"


class Estudante(Protocol):
    """passo do roteiro e historico entram, a pergunta ao paciente sai."""

    modelo: str
    versao_prompt: str

    def perguntar(self, historico: list[Turno], passo: Passo) -> str:
        """pergunta que o estudante faz neste passo.

        Args:
            historico: turnos anteriores da conversa, em ordem.
            passo: passo do roteiro da ficha.

        Returns:
            texto da pergunta.
        """
        ...


class EstudanteRoteiro:
    """le a pergunta do roteiro como esta, sem llm."""

    modelo = "estudante-roteiro"
    versao_prompt = "roteiro-literal-v1"

    @staticmethod
    def perguntar(historico: list[Turno], passo: Passo) -> str:
        """a pergunta do roteiro.

        Args:
            historico: ignorado.
            passo: passo do roteiro.

        Returns:
            a pergunta do passo.
        """
        return passo.pergunta


class SaidaEstudante(BaseModel):
    """o que o llm devolve."""

    pergunta: str = Field(min_length=1)


def modelo_do_estudante() -> str:
    """LLM_MODELO_ESTUDANTE; vazia, usa o modelo do juiz, que tem mais cota.

    Returns:
        nome do modelo do estudante.
    """
    modelo = os.environ.get("LLM_MODELO_ESTUDANTE", "").strip()
    return modelo or os.environ.get("LLM_MODELO_JUIZ", "").strip()


class EstudanteLLM:
    """llm no papel de estudante, conduzindo a entrevista pelo roteiro."""

    versao_prompt = VERSAO_PROMPT

    def __init__(self, db: Session) -> None:
        """le o modelo e o prompt uma vez.

        Args:
            db: onde o cliente do llm registra os tokens.
        """
        self.db, self.modelo = db, modelo_do_estudante()
        self.instrucao = (PASTA_PROMPTS / f"{VERSAO_PROMPT}.md").read_text(
            encoding="utf-8"
        )

    def perguntar(self, historico: list[Turno], passo: Passo) -> str:
        """reformula a pergunta do roteiro; sem saida valida, usa a original.

        Esperado e item do passo nao vao ao llm: o estudante nao sabe o que
        o paciente esconde, como na consulta de verdade.

        Args:
            historico: turnos anteriores da conversa, em ordem.
            passo: passo do roteiro.

        Returns:
            texto da pergunta.
        """
        entrada = json.dumps(
            {
                "conversa_anterior": [t.model_dump() for t in historico],
                "pergunta_do_roteiro": passo.pergunta,
            },
            ensure_ascii=False,
        )
        try:
            saida = cliente.gerar(
                self.db,
                tarefa="estudante",
                schema=SaidaEstudante,
                entrada=entrada,
                instrucao=self.instrucao,
                modelo=self.modelo,
            )
        except cliente.SaidaInvalidaError:
            return passo.pergunta
        return saida.pergunta.strip()
