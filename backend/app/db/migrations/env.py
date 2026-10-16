from alembic import context
from sqlalchemy import create_engine

from app.db import modelos  # noqa: F401  registra as tabelas no metadata
from app.db.base import Base, url_do_banco


def rodar() -> None:
    """aplica as migracoes direto no banco (sem modo offline)."""
    with create_engine(url_do_banco()).connect() as conexao:
        context.configure(connection=conexao, target_metadata=Base.metadata)
        with context.begin_transaction():
            context.run_migrations()


rodar()
