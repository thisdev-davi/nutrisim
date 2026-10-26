import pytest

from app.db.deps import obter_sessao
from app.main import app


class BancoFalso:
    """guarda em memoria o que as rotas gravam no banco."""

    def __init__(self):
        """comeca vazio e sem commit."""
        self.objetos, self.commits = [], 0

    def add(self, objeto):
        """guarda o objeto."""
        self.objetos.append(objeto)

    def commit(self):
        """so conta o commit."""
        self.commits += 1

    def get(self, modelo, id_):
        """busca pela chave primaria.

        Returns:
            objeto encontrado ou None.
        """
        return next(
            (o for o in self.objetos if isinstance(o, modelo) and o.id == id_), None
        )


@pytest.fixture
def banco():
    """troca o banco das rotas pelo falso.

    Yields:
        banco falso usado pelas rotas.
    """
    falso = BancoFalso()
    app.dependency_overrides[obter_sessao] = lambda: falso
    yield falso
    app.dependency_overrides.pop(obter_sessao, None)
