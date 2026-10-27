# paciente do eval (NS-026): o runner so conhece esta interface
# o paciente real (NS-020) entra na NS-034, embrulhando anamnese.responder
from typing import Literal, Protocol

from pydantic import BaseModel

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
