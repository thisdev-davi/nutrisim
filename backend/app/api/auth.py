from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.erros import ApiError
from app.db import modelos
from app.db.deps import obter_sessao
from app.schemas.api import RespostaErro
from app.schemas.auth import Acesso, Login, NovoUsuario, Usuario
from app.seguranca import HASH_FALSO, conferir_senha, gerar_hash, gerar_token, ler_token

router = APIRouter(
    prefix="/auth",
    tags=["autenticacao"],
    responses={422: {"model": RespostaErro}},
)
NAO_AUTORIZADO = {401: {"model": RespostaErro}}

Banco = Annotated[Session, Depends(obter_sessao)]
Credenciais = Annotated[
    HTTPAuthorizationCredentials | None, Depends(HTTPBearer(auto_error=False))
]

# o 401 avisa como autenticar (RFC 6750)
PEDE_BEARER = {"WWW-Authenticate": "Bearer"}
EMAIL_EM_USO = "ja existe uma conta com esse e-mail"


def usuario_atual(credenciais: Credenciais, db: Banco) -> modelos.Usuario:
    """exige um token valido de um usuario que ainda existe.

    Args:
        credenciais: header Authorization: Bearer, se veio.
        db: sessao do banco.

    Returns:
        usuario dono do token.

    Raises:
        ApiError: sem token, token invalido ou expirado, ou usuario apagado.
    """
    if credenciais is None:
        raise ApiError(401, "nao_autenticado", "faca login para continuar", PEDE_BEARER)
    usuario_id = ler_token(credenciais.credentials)
    usuario = db.get(modelos.Usuario, usuario_id) if usuario_id else None
    if usuario is None:
        raise ApiError(
            401, "token_invalido", "sessao expirada, faca login de novo", PEDE_BEARER
        )
    return usuario


UsuarioAtual = Annotated[modelos.Usuario, Depends(usuario_atual)]


def _acesso(usuario: modelos.Usuario) -> Acesso:
    return Acesso(token=gerar_token(usuario.id), usuario=_para_api(usuario))


def _para_api(usuario: modelos.Usuario) -> Usuario:
    return Usuario(id=str(usuario.id), nome=usuario.nome, email=usuario.email)


def _buscar_por_email(db: Session, email: str) -> modelos.Usuario | None:
    return db.scalar(select(modelos.Usuario).where(modelos.Usuario.email == email))


# def e nao async: o argon2 bloqueia, entao roda no threadpool
@router.post("/cadastro", status_code=201, responses={409: {"model": RespostaErro}})
def cadastrar(dados: NovoUsuario, db: Banco) -> Acesso:
    """cria a conta e ja devolve o token, sem pedir login logo depois.

    Args:
        dados: nome, e-mail e senha.
        db: sessao do banco.

    Returns:
        token de acesso e usuario criado.

    Raises:
        ApiError: e-mail ja cadastrado.
    """
    if _buscar_por_email(db, dados.email) is not None:
        raise ApiError(409, "email_em_uso", EMAIL_EM_USO)
    usuario = modelos.Usuario(
        id=uuid4(),  # o default do modelo so roda no flush
        nome=dados.nome,
        email=dados.email,
        senha_hash=gerar_hash(dados.senha),
    )
    # o token sai antes do commit: se falhar, a conta nao fica gravada sem o
    # estudante saber, e a nova tentativa nao esbarra no email_em_uso
    acesso = _acesso(usuario)
    db.add(usuario)
    try:
        db.commit()
    except IntegrityError as e:
        # dois cadastros simultaneos passaram pela busca; o unique segura
        db.rollback()
        raise ApiError(409, "email_em_uso", EMAIL_EM_USO) from e
    return acesso


@router.post("/login", responses=NAO_AUTORIZADO)
def entrar(dados: Login, db: Banco) -> Acesso:
    """troca e-mail e senha por um token de acesso.

    Args:
        dados: e-mail e senha.
        db: sessao do banco.

    Returns:
        token de acesso e usuario logado.

    Raises:
        ApiError: e-mail ou senha errados (a mesma resposta para os dois).
    """
    usuario = _buscar_por_email(db, dados.email)
    senha_hash = usuario.senha_hash if usuario else HASH_FALSO
    if not conferir_senha(senha_hash, dados.senha) or usuario is None:
        raise ApiError(
            401, "credenciais_invalidas", "e-mail ou senha incorretos", PEDE_BEARER
        )
    return _acesso(usuario)


@router.get("/eu", responses=NAO_AUTORIZADO)
def ler_usuario(usuario: UsuarioAtual) -> Usuario:
    """usuario dono do token, para o front saber quem esta logado.

    Args:
        usuario: usuario autenticado.

    Returns:
        dados do usuario, sem a senha.
    """
    return _para_api(usuario)
