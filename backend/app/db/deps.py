"""Dependências de acesso ao banco."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import url_do_banco


def obter_sessao() -> Generator[Session, None, None]:
    """Abre uma sessão do banco para uma requisição.

    Yields:
        Sessão SQLAlchemy aberta para a requisição.
    """
    engine = create_engine(url_do_banco())
    try:
        with Session(engine) as sessao:
            yield sessao
    finally:
        engine.dispose()
