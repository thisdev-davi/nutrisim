"""Dependências de acesso ao banco."""

from collections.abc import Generator
from functools import cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from app.db.base import url_do_banco


@cache
def obter_engine() -> Engine:
    """cria o engine uma vez, somente quando o banco for usado.

    Returns:
        engine compartilhado pelas sessões da aplicação.
    """
    return create_engine(url_do_banco())


def obter_sessao() -> Generator[Session, None, None]:
    """Abre uma sessão do banco para uma requisição.

    Yields:
        Sessão SQLAlchemy aberta para a requisição.
    """
    with Session(obter_engine()) as sessao:
        yield sessao
