from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.api.auth import usuario_atual
from app.db.deps import obter_sessao
from app.db.modelos import ChamadaLLM, Sessao, Usuario
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
        """conta o commit, numera e data as mensagens, como faria o insert."""
        self.commits += 1
        for objeto in self.objetos:
            if isinstance(objeto, Sessao):
                objeto.criada_em = objeto.criada_em or datetime.now(UTC)
            for i, mensagem in enumerate(getattr(objeto, "mensagens", []), 1):
                mensagem.id = mensagem.id or i
                mensagem.criada_em = mensagem.criada_em or datetime.now(UTC)

    def rollback(self):
        """nada a desfazer: o falso nao tem transacao."""

    def refresh(self, objeto, **kwargs):
        """nada a recarregar: tudo ja esta em memoria."""

    def scalars(self, consulta):
        """objetos que casam com um where de igualdade (coluna == valor).

        Ignora order_by e limit: devolve do ultimo gravado para o primeiro,
        como o order_by criada_em desc das rotas.

        Returns:
            objetos encontrados.
        """
        modelo = consulta.column_descriptions[0]["entity"]
        filtro = consulta.whereclause
        return [
            o
            for o in reversed(self.objetos)
            if isinstance(o, modelo)
            and getattr(o, filtro.left.key) == filtro.right.value
        ]

    def scalar(self, consulta):
        """primeiro objeto que casa com um where de igualdade.

        Returns:
            objeto encontrado ou None.
        """
        return next(iter(self.scalars(consulta)), None)

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
def usuario():
    """pula o token: as rotas protegidas recebem este usuario.

    A autenticacao em si e testada em test_auth.py.

    Yields:
        usuario logado nas rotas.
    """
    logado = Usuario(id=uuid4(), nome="Ana", email="ana@exemplo.com", senha_hash="")
    app.dependency_overrides[usuario_atual] = lambda: logado
    yield logado
    app.dependency_overrides.pop(usuario_atual, None)


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
