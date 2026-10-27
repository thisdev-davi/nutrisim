import pytest

from app.db.deps import obter_sessao
from app.db.modelos import ChamadaLLM
from app.eval import juiz, runner
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
        """conta o commit e numera as mensagens, como faria o insert."""
        self.commits += 1
        for objeto in self.objetos:
            for i, mensagem in enumerate(getattr(objeto, "mensagens", []), 1):
                mensagem.id = mensagem.id or i

    def refresh(self, objeto, **kwargs):
        """nada a recarregar: tudo ja esta em memoria."""

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


@pytest.fixture
def julgados(monkeypatch):
    """troca o juiz por um que acha contradicao so no turno 2.

    Returns:
        lista com o tamanho da conversa em cada julgamento.
    """
    monkeypatch.setenv("LLM_MODELO", "modelo-paciente")
    monkeypatch.setenv("LLM_MODELO_JUIZ", "modelo-juiz")
    chamadas = []

    def julgar(db, *, ficha, conversa):
        chamadas.append(len(conversa))
        uso = {"tokens_entrada": 10, "tokens_saida": 2}
        db.add(ChamadaLLM(tarefa="juiz", modelo="m", tentativa=1, **uso))
        categoria = "contradicao" if len(conversa) == 2 else "consistente"  # noqa: PLR2004
        return juiz.Veredito(
            turno=len(conversa), categoria=categoria, justificativa="j"
        )

    monkeypatch.setattr(runner.juiz, "julgar", julgar)
    return chamadas
