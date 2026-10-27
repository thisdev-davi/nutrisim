# paciente do eval (NS-026): o runner so conhece esta interface
# o real embrulha anamnese.responder (NS-020); o falso serve para testar o runner
import os
from typing import Literal, Protocol

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api import anamnese
from app.db import modelos
from app.eval.juiz import Turno
from app.schemas.ficha import Ficha

Esperado = Literal["revelar", "omitir", "recusar"]


class Passo(BaseModel):
    """uma pergunta do roteiro da ficha de eval."""

    pergunta: str
    esperado: Esperado | None
    item: str | None


class FichaEval(BaseModel):
    """arquivo de evals/fichas: ficha oculta e roteiro."""

    id: str
    ficha: Ficha
    roteiro: list[Passo]


class Paciente(Protocol):
    """pergunta e historico entram, a fala do paciente sai."""

    modelo: str
    versao_prompt: str

    def responder(self, historico: list[Turno], pergunta: str) -> str:
        """fala do paciente para a pergunta nova.

        Args:
            historico: turnos anteriores da conversa, em ordem.
            pergunta: pergunta nova do estudante.

        Returns:
            texto da fala.
        """
        ...


NEUTRA = "Ah, é o normal do dia a dia, nada de diferente."
RECUSA = "Isso eu não sei te dizer, quem entende disso é você."


class PacienteFalso:
    """respostas fixas tiradas do roteiro, sem llm; serve para testar o runner."""

    modelo = "paciente-falso"
    versao_prompt = "respostas-fixas-v1"

    def __init__(self, ficha: FichaEval) -> None:
        """monta uma resposta para cada pergunta do roteiro.

        Args:
            ficha: ficha de eval com o roteiro.
        """
        self.respostas = {p.pergunta: self._resposta(p) for p in ficha.roteiro}

    @staticmethod
    def _resposta(passo: Passo) -> str:
        if passo.esperado == "revelar":
            return f"Ah, isso eu não tinha falado: {passo.item}."
        if passo.esperado == "recusar":
            return RECUSA
        return NEUTRA

    def responder(self, historico: list[Turno], pergunta: str) -> str:
        """resposta fixa da pergunta; fora do roteiro, a neutra.

        Args:
            historico: ignorado, as respostas nao dependem dele.
            pergunta: pergunta do estudante.

        Returns:
            texto da fala.
        """
        return self.respostas.get(pergunta, NEUTRA)


class PacienteReal:
    """o paciente simulado do backend, chamado direto, sem a rota nem o banco."""

    versao_prompt = anamnese.PROMPT.stem

    def __init__(self, ficha: FichaEval, db: Session) -> None:
        """guarda so a parte do paciente: restricoes e gabarito nao chegam ao llm.

        Args:
            ficha: ficha de eval.
            db: onde o cliente do llm registra os tokens.
        """
        self.paciente, self.db = ficha.ficha.paciente, db
        self.modelo = os.environ["LLM_MODELO"]

    def responder(self, historico: list[Turno], pergunta: str) -> str:
        """fala do paciente, com o historico no formato da anamnese.

        Args:
            historico: turnos anteriores da conversa, em ordem.
            pergunta: pergunta nova do estudante.

        Returns:
            texto da fala.
        """
        mensagens = []
        for t in historico:
            mensagens += [
                modelos.Mensagem(autor="estudante", texto=t.pergunta),
                modelos.Mensagem(autor="paciente", texto=t.resposta),
            ]
        return anamnese.responder(self.db, self.paciente, mensagens, pergunta)
