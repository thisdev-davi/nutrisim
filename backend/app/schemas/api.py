# contrato da api com o front (etapas 1 e 2)
# nenhum modelo aqui carrega a ficha oculta: ela nunca sai do backend
from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Dificuldade(StrEnum):
    """niveis de dificuldade do caso."""

    FACIL = "facil"
    MEDIO = "medio"
    DIFICIL = "dificil"


class Etapa(StrEnum):
    """etapa atual da sessao (as demais entram com as etapas 3 a 5)."""

    ANAMNESE = "anamnese"
    PLANO = "plano"


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
