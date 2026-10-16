# ficha oculta do caso (NS-014), campos de content/perfis.md
# o prompt do paciente recebe so `paciente`; `gabarito` vai so para rubrica e eval
from typing import Literal, Self

from pydantic import BaseModel, Field, model_validator

from app.schemas.api import Dificuldade


class Omissao(BaseModel):
    """informacao que o paciente so revela diante do gatilho."""

    informacao: str
    gatilho: str = Field(description="pergunta ou tema que faz o paciente revelar")


class FichaPaciente(BaseModel):
    """tudo que o paciente simulado sabe sobre si."""

    nome: str
    idade: int = Field(ge=18, le=100)
    genero: Literal["feminino", "masculino"]
    queixa_principal: str
    peso_kg: float = Field(gt=0)
    altura_cm: float = Field(gt=0)
    # nivel usado no calculo do GET (NS-024)
    atividade_fisica: Literal["sedentario", "leve", "moderado", "intenso"]
    orcamento_mensal_reais: float = Field(gt=0, description="gasto com alimentacao")
    rotina: str
    quem_cozinha: str
    cultura_alimentar: str
    preferencias: list[str]
    aversoes: list[str]
    recordatorio: list[str] = Field(description="refeicoes de um dia tipico")
    postura: Literal["colaborativa", "ambivalente", "resistente"]
    forma_de_responder: str
    imprecisoes: list[str] = Field(
        description="erro previsto no relato, nao contradicao"
    )
    omissoes: list[Omissao]


class Restricoes(BaseModel):
    """limites que o motor confere no plano; o paciente nao conhece os numeros."""

    sodio_max_mg: float | None = Field(default=None, gt=0)
    fibras_min_g_por_1000kcal: float | None = Field(default=None, gt=0)
    gordura_saturada_max_pct_vet: float | None = Field(default=None, gt=0, le=100)
    proteina_g_kg_min: float | None = Field(default=None, gt=0)
    proteina_g_kg_max: float | None = Field(default=None, gt=0)
    alimentos_evitados: list[str] = []

    @model_validator(mode="after")
    def faixa_de_proteina(self) -> Self:
        """minimo acima do maximo deixaria todo plano invalido.

        Returns:
            as restricoes validadas.

        Raises:
            ValueError: minimo de proteina maior que o maximo.
        """
        lo, hi = self.proteina_g_kg_min, self.proteina_g_kg_max
        if lo is not None and hi is not None and lo > hi:
            raise ValueError("proteina_g_kg_min maior que proteina_g_kg_max")
        return self


class Gabarito(BaseModel):
    """o que a avaliacao espera; nunca entra no prompt do paciente."""

    conduta_esperada: Literal["plano", "encaminhamento"]
    sinais_de_alerta: list[str]
    o_que_investigar: list[str] = Field(description="o que a anamnese devia achar")


class Ficha(BaseModel):
    """ficha oculta completa, gerada pela NS-019 e guardada so no backend."""

    perfil_id: str
    dificuldade: Dificuldade
    paciente: FichaPaciente
    restricoes: Restricoes
    gabarito: Gabarito
