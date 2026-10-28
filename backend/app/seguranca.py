# hash de senha e token de acesso (NS-035)
import os
from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

ALGORITMO = "HS256"
VALIDADE = timedelta(hours=8)
# o minimo recomendado para HS256 (RFC 7518, secao 3.2)
SEGREDO_MINIMO_BYTES = 32

# argon2id com os parametros padrao da biblioteca (RFC 9106)
_hasher = PasswordHasher()


def gerar_hash(senha: str) -> str:
    """gera o hash argon2id da senha, com sal aleatorio.

    Args:
        senha: senha em texto puro.

    Returns:
        hash no formato PHC, com os parametros e o sal embutidos.
    """
    return _hasher.hash(senha)


def conferir_senha(senha_hash: str, senha: str) -> bool:
    """confere a senha com o hash salvo.

    Args:
        senha_hash: hash salvo no banco.
        senha: senha digitada no login.

    Returns:
        True se a senha confere.
    """
    try:
        return _hasher.verify(senha_hash, senha)
    except (VerifyMismatchError, InvalidHashError):
        return False


# usado quando o e-mail nao existe: o login confere a senha mesmo assim, para o
# tempo de resposta nao revelar quem tem cadastro. calculado na carga, senao o
# primeiro login com e-mail inexistente roda o argon2 duas vezes
HASH_FALSO = gerar_hash("senha-de-ninguem")


def segredo() -> str:
    """le a chave que assina os tokens.

    Returns:
        valor de JWT_SECRET.

    Raises:
        RuntimeError: chave ausente ou curta; com ela vazia, qualquer um forjaria
            um token.
    """
    valor = os.environ.get("JWT_SECRET", "")
    if len(valor.encode()) < SEGREDO_MINIMO_BYTES:
        raise RuntimeError(
            f"JWT_SECRET ausente ou com menos de {SEGREDO_MINIMO_BYTES} bytes; "
            "gere uma com: openssl rand -hex 32"
        )
    return valor


def gerar_token(usuario_id: UUID) -> str:
    """assina um token de acesso para o usuario.

    Args:
        usuario_id: id do usuario autenticado.

    Returns:
        jwt assinado, valido por VALIDADE.
    """
    agora = datetime.now(UTC)
    dados = {"sub": str(usuario_id), "iat": agora, "exp": agora + VALIDADE}
    return jwt.encode(dados, segredo(), algorithm=ALGORITMO)


def ler_token(token: str) -> UUID | None:
    """valida assinatura e validade do token.

    Args:
        token: jwt recebido no header Authorization.

    Returns:
        id do usuario, ou None se o token for invalido ou tiver expirado.
    """
    try:
        dados = jwt.decode(
            token,
            segredo(),
            algorithms=[ALGORITMO],  # fixo: nao aceita o "alg" que vier no token
            options={"require": ["sub", "exp"]},
        )
        return UUID(dados["sub"])
    except (jwt.InvalidTokenError, ValueError):
        return None
