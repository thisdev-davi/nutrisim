# tabelas do banco; cada card acrescenta as suas com uma migracao nova
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

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
