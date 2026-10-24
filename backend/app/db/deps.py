"""dependencias de acesso ao banco."""

from collections.abc import Generator
from functools import cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from app.db.base import url_do_banco


@cache
def obter_engine() -> Engine:
    """cria o engine uma vez, somente quando o banco for usado.

    Returns:
        engine compartilhado pelas sessoes da aplicacao.
    """
    return create_engine(url_do_banco(), pool_pre_ping=True)  # neon fecha ociosas


def obter_sessao() -> Generator[Session, None, None]:
    """abre uma sessao do banco para uma requisicao.

    Yields:
        sessao SQLAlchemy aberta para a requisicao.
    """
    with Session(obter_engine()) as sessao:
        yield sessao
