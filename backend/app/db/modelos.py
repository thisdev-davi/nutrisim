# tabelas do banco; cada card acrescenta as suas com uma migracao nova
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Sessao(Base):
    """sessao de atendimento; a ficha oculta fica aqui e nunca vai ao front."""

    __tablename__ = "sessoes"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    perfil_id: Mapped[str]
    dificuldade: Mapped[str]
    etapa: Mapped[str]
    ficha: Mapped[dict] = mapped_column(JSONB)
    criada_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # pelo id, e nao pelo criada_em: pergunta e fala saem na mesma transacao
    mensagens: Mapped[list["Mensagem"]] = relationship(order_by="Mensagem.id")


class Mensagem(Base):
    """uma fala da anamnese, do estudante ou do paciente."""

    __tablename__ = "mensagens"

    id: Mapped[int] = mapped_column(primary_key=True)
    sessao_id: Mapped[UUID] = mapped_column(ForeignKey("sessoes.id"), index=True)
    autor: Mapped[str]
    texto: Mapped[str]
    criada_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class ChamadaLLM(Base):
    """uma chamada ao llm, com os tokens gastos; cada nova tentativa conta."""

    __tablename__ = "chamadas_llm"

    id: Mapped[int] = mapped_column(primary_key=True)
    # vazio fora de uma sessao (eval, por exemplo)
    sessao_id: Mapped[UUID | None] = mapped_column(ForeignKey("sessoes.id"))
    tarefa: Mapped[str]
    modelo: Mapped[str]
    tentativa: Mapped[int]
    tokens_entrada: Mapped[int]
    tokens_saida: Mapped[int]
    criada_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Alimentos(Base):
    """tabela referente aos dados dos alimentos."""

    __tablename__ = "alimentos"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"))
    nome: Mapped[str]


class Nutrientes(Base):
    """tabela referente aos dados nutricionais dos alimentos."""

    __tablename__ = "nutrientes"

    id: Mapped[int] = mapped_column(ForeignKey("alimentos.id"), primary_key=True)
    umidade: Mapped[float | None]
    kcal: Mapped[float | None]
    kj: Mapped[float | None]
    proteina: Mapped[float | None]
    lipidios: Mapped[float | None]
    colesterol: Mapped[float | None]
    carboidratos: Mapped[float | None]
    fibra_alimentar: Mapped[float | None]
    cinzas: Mapped[float | None]
    calcio: Mapped[float | None]
    magnesio: Mapped[float | None]
    manganes: Mapped[float | None]
    fosforo: Mapped[float | None]
    ferro: Mapped[float | None]
    sodio: Mapped[float | None]
    potassio: Mapped[float | None]
    cobre: Mapped[float | None]
    zinco: Mapped[float | None]
    retinol: Mapped[float | None]
    re: Mapped[float | None]
    rae: Mapped[float | None]
    tiamina: Mapped[float | None]
    riboflavina: Mapped[float | None]
    piridoxina: Mapped[float | None]
    niacina: Mapped[float | None]
    vitamina_c: Mapped[float | None]


class AcidosGraxos(Base):
    """tabela referente aos dados de acidos graxos dos alimentos."""

    __tablename__ = "acidos_graxos"

    id: Mapped[int] = mapped_column(ForeignKey("alimentos.id"), primary_key=True)
    gordura_saturada: Mapped[float | None]
    gordura_monoinsaturada: Mapped[float | None]
    gordura_poliinsaturada: Mapped[float | None]
    acido_laurico: Mapped[float | None]
    acido_miristico: Mapped[float | None]
    acido_palmitico: Mapped[float | None]
    acido_estearico: Mapped[float | None]
    acido_araquidico: Mapped[float | None]
    acido_behenico: Mapped[float | None]
    acido_lignocerico: Mapped[float | None]
    acido_miristoleico: Mapped[float | None]
    acido_palmitoleico: Mapped[float | None]
    acido_oleico: Mapped[float | None]
    acido_eicosenoico: Mapped[float | None]
    acido_linoleico: Mapped[float | None]
    acido_linolenico: Mapped[float | None]
    acido_araquidonico: Mapped[float | None]
    acido_epa: Mapped[float | None]
    acido_dpa: Mapped[float | None]
    acido_dha: Mapped[float | None]
    acido_oleico_trans: Mapped[float | None]
    acido_linoleico_trans: Mapped[float | None]


class Categorias(Base):
    """tabela que representa as categorias dos alimentos."""

    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str]
