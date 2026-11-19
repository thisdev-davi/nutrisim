# contrato da api com o front (etapas 1 e 2)
# nenhum modelo aqui carrega a ficha oculta: ela nunca sai do backend
from datetime import datetime
from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Dificuldade(StrEnum):
    """niveis de dificuldade do caso."""

    FACIL = "facil"
    MEDIO = "medio"
    DIFICIL = "dificil"


class Etapa(StrEnum):
    """etapa atual da sessao (o retorno entra com a etapa 5)."""

    ANAMNESE = "anamnese"
    PLANO = "plano"
    CENARIOS = "cenarios"


class Perfil(BaseModel):
    """perfil de paciente que o estudante pode escolher."""

    id: str
    nome: str
    descricao: str


class Opcoes(BaseModel):
    """o que a tela de selecao mostra."""

    perfis: list[Perfil]
    dificuldades: list[Dificuldade]


class NovaSessao(BaseModel):
    """escolha do estudante na etapa 1."""

    perfil_id: str
    dificuldade: Dificuldade


class Paciente(BaseModel):
    """so o que o estudante pode ver do paciente."""

    nome: str
    idade: int
    queixa_principal: str


class Mensagem(BaseModel):
    """uma fala da anamnese."""

    id: str
    autor: Literal["estudante", "paciente"]
    texto: str
    criada_em: datetime


class Sessao(BaseModel):
    """estado da sessao, usado para criar e para retomar."""

    id: str
    etapa: Etapa
    perfil_id: str
    dificuldade: Dificuldade
    paciente: Paciente
    mensagens: list[Mensagem]


class ResumoSessao(BaseModel):
    """o que o inicio mostra de cada sessao, sem as falas."""

    id: str
    etapa: Etapa
    perfil: str
    dificuldade: Dificuldade
    paciente: Paciente
    criada_em: datetime


class NovaMensagem(BaseModel):
    """pergunta do estudante ao paciente."""

    model_config = ConfigDict(str_strip_whitespace=True)  # "   " vira vazio

    texto: str = Field(min_length=1, max_length=2000)


class EtapaAtual(BaseModel):
    """resposta ao encerrar uma etapa."""

    etapa: Etapa


# eventos do stream (sse): varios "trecho", depois "fim" ou "erro"
class Trecho(BaseModel):
    """pedaco da fala do paciente."""

    texto: str


class Fim(BaseModel):
    """fala completa e salva."""

    mensagem_id: str


class Erro(BaseModel):
    """erro padrao: o front decide o que exibir pelo codigo."""

    codigo: str
    mensagem: str


class RespostaErro(BaseModel):
    """corpo de toda resposta de erro."""

    erro: Erro


# etapa 3: plano alimentar (NS-041, NS-044). o front manda so ids e gramas;
# todo numero da resposta sai do motor
class ItemPlano(BaseModel):
    """alimento da TACO com a porcao escolhida."""

    alimento_id: int
    gramas: float = Field(gt=0, le=2000)


class RefeicaoPlano(BaseModel):
    """uma refeicao do plano, como o estudante montou."""

    model_config = ConfigDict(str_strip_whitespace=True)

    nome: str = Field(min_length=1, max_length=40)
    itens: list[ItemPlano] = Field(max_length=30)


class NovoPlano(BaseModel):
    """corpo do PUT: o plano inteiro, a cada mudanca."""

    refeicoes: list[RefeicaoPlano] = Field(min_length=1, max_length=8)

    @model_validator(mode="after")
    def nomes_unicos(self) -> Self:
        """o nome identifica a refeicao nas violacoes e nas trocas do cenario.

        Returns:
            o plano validado.

        Raises:
            ValueError: duas refeicoes com o mesmo nome.
        """
        nomes = [r.nome.casefold() for r in self.refeicoes]
        if len(nomes) != len(set(nomes)):
            raise ValueError("refeicoes com nome repetido")
        return self


class Nutrientes(BaseModel):
    """soma de nutrientes; sem_dado lista os alimentos com NA na TACO."""

    valores: dict[str, float]
    sem_dado: dict[str, list[str]]


class AdequacaoNutriente(BaseModel):
    """consumo de um nutriente comparado a DRI (motor/adequacao.py)."""

    consumo: float
    referencia: float
    percentual: float
    classificacao: Literal["abaixo", "adequado", "acima"]
    sem_dado: list[str]


class Violacao(BaseModel):
    """restricao do caso que o plano nao cumpre (NS-044)."""

    tipo: Literal[
        "sodio",
        "fibras",
        "gordura_saturada",
        "proteina",
        "alimento_evitado",
        "orcamento",
    ]
    mensagem: str
    # aponta a causa para a tela marcar o item; None quando e do dia todo
    refeicao: str | None = None
    alimento_id: int | None = None


class ItemCalculado(ItemPlano):
    """item com o nome e a contribuicao dele."""

    nome: str
    kcal: float


class RefeicaoCalculada(BaseModel):
    """refeicao com os itens e a composicao calculada."""

    nome: str
    itens: list[ItemCalculado]
    composicao: Nutrientes


class Plano(BaseModel):
    """plano salvo, com tudo que o motor calculou."""

    refeicoes: list[RefeicaoCalculada]
    total: Nutrientes
    get_kcal: float
    adequacao: dict[str, AdequacaoNutriente]
    violacoes: list[Violacao]
    custo_diario_reais: float
    # alimentos sem preco na tabela: o custo acima esta incompleto (NS-043)
    sem_preco: list[str]


# etapa 4: cenarios ideal e realista (NS-045, NS-046)
class PontoSemana(BaseModel):
    """peso projetado no fim de uma semana."""

    semana: int = Field(ge=0)
    peso_kg: float


class Cenario(BaseModel):
    """consumo projetado; a adequacao e do consumo medio do cenario."""

    peso: list[PontoSemana]
    adequacao: dict[str, AdequacaoNutriente]


class AdesaoRefeicao(BaseModel):
    """quanto da refeicao o paciente segue (estimado pelo llm)."""

    refeicao: str
    adesao: float = Field(ge=0, le=1)


class Substituicao(BaseModel):
    """troca provavel, sempre entre alimentos da TACO."""

    refeicao: str
    original_id: int
    original: str
    substituto_id: int
    substituto: str
    motivo: str


class CenarioRealista(Cenario):
    """cenario com a adesao e as trocas que o llm estimou."""

    adesao: list[AdesaoRefeicao]
    substituicoes: list[Substituicao]


class Cenarios(BaseModel):
    """resposta da etapa 4."""

    ideal: Cenario
    realista: CenarioRealista
    aviso: str = Field(description="limitacao da projecao, sempre visivel")
