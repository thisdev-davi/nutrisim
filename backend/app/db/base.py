# base dos modelos e url do banco (neon em dev e prod)
import os

from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """base de todos os modelos do banco."""


def url_do_banco() -> str:
    """le DATABASE_URL e forca o driver psycopg 3.

    O Neon entrega a url como postgresql://, que o SQLAlchemy liga ao psycopg2.

    Returns:
        url pronta para o SQLAlchemy.
    """
    url = make_url(os.environ["DATABASE_URL"])
    return url.set(drivername="postgresql+psycopg").render_as_string(
        hide_password=False
    )
