from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.db.modelos import Sessao, Usuario
from app.main import app
from app.seguranca import conferir_senha, gerar_hash, gerar_token, segredo
from tests.test_cliente_llm import provedor_falso
from tests.test_ficha import EXEMPLO

client = TestClient(app=app)
SEGREDO = "segredo-de-teste-com-mais-de-32-bytes"
ANA = {"nome": "Ana Souza", "email": "ana@exemplo.com", "senha": "senha-forte-123"}

# toda rota da simulacao, com um corpo valido para nao cair no 422
PROTEGIDAS = [
    ("get", "/api/perfis", None),
    ("get", "/api/alimentos?nome=arroz", None),
    (
        "post",
        "/api/sessoes",
        {"perfil_id": "adulto-hipertensao", "dificuldade": "facil"},
    ),
    ("get", f"/api/sessoes/{uuid4()}", None),
    ("post", f"/api/sessoes/{uuid4()}/mensagens", {"texto": "oi"}),
    ("post", f"/api/sessoes/{uuid4()}/anamnese/encerrar", None),
    ("get", "/api/auth/eu", None),
]


@pytest.fixture(autouse=True)
def chave_de_teste(monkeypatch):
    """chave de assinatura dos tokens, lida do ambiente."""
    monkeypatch.setenv("JWT_SECRET", SEGREDO)


def cabecalho(token: str) -> dict[str, str]:
    """header Authorization com o token.

    Returns:
        cabecalho pronto para a requisicao.
    """
    return {"Authorization": f"Bearer {token}"}


def cadastrar(dados: dict = ANA) -> dict:
    """cadastra e devolve o corpo da resposta.

    Returns:
        token e usuario criados.
    """
    resposta = client.post("/api/auth/cadastro", json=dados)
    assert resposta.status_code == status.HTTP_201_CREATED
    return resposta.json()


def test_hash_argon2id_com_sal_aleatorio():
    """a mesma senha gera hashes diferentes, e so a senha certa confere."""
    primeiro, segundo = gerar_hash("senha-forte-123"), gerar_hash("senha-forte-123")
    assert primeiro.startswith("$argon2id$")
    assert primeiro != segundo
    assert conferir_senha(primeiro, "senha-forte-123")
    assert not conferir_senha(primeiro, "senha-errada")
    assert not conferir_senha("nao-e-hash", "senha-forte-123")


def test_cadastro_devolve_token_e_guarda_so_o_hash(banco):
    """a resposta traz o token e o usuario; o banco nunca ve a senha pura."""
    resposta = client.post("/api/auth/cadastro", json=ANA)
    assert resposta.status_code == status.HTTP_201_CREATED
    corpo = resposta.json()
    assert corpo["usuario"]["nome"] == ANA["nome"]
    assert corpo["usuario"]["email"] == ANA["email"]
    assert ANA["senha"] not in resposta.text

    (linha,) = [o for o in banco.objetos if isinstance(o, Usuario)]
    assert linha.senha_hash.startswith("$argon2id$")
    assert ANA["senha"] not in linha.senha_hash
    assert str(linha.id) == corpo["usuario"]["id"]

    eu = client.get("/api/auth/eu", headers=cabecalho(corpo["token"]))
    assert eu.status_code == status.HTTP_200_OK
    assert eu.json() == corpo["usuario"]


@pytest.mark.usefixtures("banco")
def test_email_ignora_maiusculas_no_cadastro_e_no_login():
    """quem se cadastra com maiuscula entra digitando de qualquer jeito."""
    cadastrado = cadastrar(ANA | {"email": "Ana@Exemplo.COM"})
    assert cadastrado["usuario"]["email"] == "ana@exemplo.com"
    login = client.post(
        "/api/auth/login", json={"email": "ANA@exemplo.com", "senha": ANA["senha"]}
    )
    assert login.status_code == status.HTTP_200_OK


@pytest.mark.usefixtures("banco")
def test_senha_com_espacos_vale_como_foi_digitada():
    """so o nome e aparado; a senha com espacos nas pontas entra no login."""
    senha = "  senha-forte-123 "
    cadastrado = cadastrar(ANA | {"nome": "  Ana Souza  ", "senha": senha})
    assert cadastrado["usuario"]["nome"] == "Ana Souza"
    certa = client.post("/api/auth/login", json={"email": ANA["email"], "senha": senha})
    assert certa.status_code == status.HTTP_200_OK
    aparada = client.post(
        "/api/auth/login", json={"email": ANA["email"], "senha": senha.strip()}
    )
    assert aparada.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize("valor", [None, "", "curta-demais"])
def test_segredo_ausente_ou_curto_impede_a_api_de_subir(monkeypatch, valor):
    """com a chave vazia qualquer um forjaria token: a api nem sobe."""
    if valor is None:
        monkeypatch.delenv("JWT_SECRET")
    else:
        monkeypatch.setenv("JWT_SECRET", valor)
    with pytest.raises(RuntimeError, match="JWT_SECRET"):
        segredo()
    # o with roda o lifespan, como o fastapi dev e o deploy
    with pytest.raises(RuntimeError, match="JWT_SECRET"), TestClient(app):
        pass


def test_cadastro_sem_token_nao_grava_o_usuario(monkeypatch, banco):
    """se o token falha, nada e gravado e a nova tentativa nao da 409."""
    monkeypatch.delenv("JWT_SECRET")
    falhou = client.post("/api/auth/cadastro", json=ANA)
    assert falhou.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert banco.commits == 0

    monkeypatch.setenv("JWT_SECRET", SEGREDO)
    cadastrar()


@pytest.mark.usefixtures("banco")
def test_cadastro_com_email_repetido_da_409():
    """um e-mail, uma conta, mesmo mudando a caixa."""
    cadastrar()
    repetido = client.post(
        "/api/auth/cadastro", json=ANA | {"email": "ANA@exemplo.com"}
    )
    assert repetido.status_code == status.HTTP_409_CONFLICT
    assert repetido.json()["erro"]["codigo"] == "email_em_uso"


@pytest.mark.usefixtures("banco")
@pytest.mark.parametrize(
    "invalido",
    [
        {"nome": "   "},
        {"email": "nao-e-email"},
        {"senha": "curta"},
        {"senha": "x" * 129},
    ],
)
def test_cadastro_com_dados_invalidos_da_422(invalido):
    """nome em branco, e-mail malformado e senha fora do tamanho sao barrados."""
    resposta = client.post("/api/auth/cadastro", json=ANA | invalido)
    assert resposta.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert resposta.json()["erro"]["codigo"] == "dados_invalidos"


@pytest.mark.usefixtures("banco")
def test_login_devolve_token_que_abre_as_rotas():
    """o token do login autentica nas rotas protegidas."""
    cadastrar()
    login = client.post(
        "/api/auth/login", json={"email": ANA["email"], "senha": ANA["senha"]}
    )
    assert login.status_code == status.HTTP_200_OK
    token = login.json()["token"]
    perfis = client.get("/api/perfis", headers=cabecalho(token))
    assert perfis.status_code == status.HTTP_200_OK


@pytest.mark.usefixtures("banco")
@pytest.mark.parametrize(
    "credenciais",
    [
        {"email": ANA["email"], "senha": "senha-errada"},
        {"email": "ninguem@exemplo.com", "senha": ANA["senha"]},
    ],
)
def test_login_errado_nao_revela_se_o_email_existe(credenciais):
    """senha errada e e-mail sem conta dao a mesma resposta."""
    cadastrar()
    resposta = client.post("/api/auth/login", json=credenciais)
    assert resposta.status_code == status.HTTP_401_UNAUTHORIZED
    assert resposta.json() == {
        "erro": {
            "codigo": "credenciais_invalidas",
            "mensagem": "e-mail ou senha incorretos",
        }
    }
    assert "token" not in resposta.text
    assert resposta.headers["www-authenticate"] == "Bearer"


@pytest.mark.usefixtures("banco")
@pytest.mark.parametrize(("metodo", "url", "corpo"), PROTEGIDAS)
def test_rota_protegida_sem_token_da_401(metodo, url, corpo):
    """sem o header Authorization nenhuma rota da simulacao responde."""
    resposta = client.request(metodo, url, json=corpo)
    assert resposta.status_code == status.HTTP_401_UNAUTHORIZED
    assert resposta.json()["erro"]["codigo"] == "nao_autenticado"
    assert resposta.headers["www-authenticate"] == "Bearer"


def token_expirado(usuario_id: str) -> str:
    """token bem assinado, mas vencido.

    Returns:
        jwt expirado.
    """
    passado = datetime.now(UTC) - timedelta(hours=1)
    return jwt.encode({"sub": usuario_id, "exp": passado}, SEGREDO, algorithm="HS256")


def token_outra_chave(usuario_id: str) -> str:
    """token assinado com outra chave.

    Returns:
        jwt com assinatura invalida.
    """
    futuro = datetime.now(UTC) + timedelta(hours=1)
    outra = "outra-chave-que-tambem-tem-32-bytes"
    return jwt.encode({"sub": usuario_id, "exp": futuro}, outra, algorithm="HS256")


def token_sem_assinatura(usuario_id: str) -> str:
    """token com "alg": "none", que nao pode ser aceito.

    Returns:
        jwt sem assinatura.
    """
    futuro = datetime.now(UTC) + timedelta(hours=1)
    return jwt.encode({"sub": usuario_id, "exp": futuro}, None, algorithm="none")


@pytest.mark.usefixtures("banco")
@pytest.mark.parametrize(
    "forjar",
    [
        token_expirado,
        token_outra_chave,
        token_sem_assinatura,
        lambda _: "nao-e-um-jwt",
        lambda _: gerar_token(uuid4()),  # usuario que nao existe (ou foi apagado)
    ],
)
def test_token_invalido_da_401(forjar):
    """expirado, adulterado, sem assinatura ou de usuario inexistente: negado."""
    usuario_id = cadastrar()["usuario"]["id"]
    resposta = client.get("/api/perfis", headers=cabecalho(forjar(usuario_id)))
    assert resposta.status_code == status.HTTP_401_UNAUTHORIZED
    assert resposta.json()["erro"]["codigo"] == "token_invalido"
    assert resposta.headers["www-authenticate"] == "Bearer"


def test_sessao_fica_com_o_dono_e_outro_estudante_nao_acessa(monkeypatch, banco):
    """a sessao nasce ligada a quem criou; para os demais ela nao existe."""
    provedor_falso(monkeypatch, [EXEMPLO])
    ana = cabecalho(cadastrar()["token"])
    beto = cabecalho(cadastrar(ANA | {"email": "beto@exemplo.com"})["token"])

    nova = {"perfil_id": "adulto-hipertensao", "dificuldade": "facil"}
    criada = client.post("/api/sessoes", json=nova, headers=ana)
    assert criada.status_code == status.HTTP_201_CREATED
    sessao_id = criada.json()["id"]
    (linha,) = [o for o in banco.objetos if isinstance(o, Sessao)]
    usuarios = {o.email: o.id for o in banco.objetos if isinstance(o, Usuario)}
    assert linha.usuario_id == usuarios[ANA["email"]]

    assert client.get(f"/api/sessoes/{sessao_id}", headers=ana).status_code == (
        status.HTTP_200_OK
    )
    for metodo, url, corpo in [
        ("get", f"/api/sessoes/{sessao_id}", None),
        ("post", f"/api/sessoes/{sessao_id}/mensagens", {"texto": "oi"}),
        ("post", f"/api/sessoes/{sessao_id}/anamnese/encerrar", None),
    ]:
        alheia = client.request(metodo, url, json=corpo, headers=beto)
        assert alheia.status_code == status.HTTP_404_NOT_FOUND
        assert alheia.json()["erro"]["codigo"] == "sessao_nao_encontrada"
