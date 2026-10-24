from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.exceptions import HTTPException

from app.schemas.api import Erro, RespostaErro


class ApiError(Exception):
    """erro com codigo estavel para o front."""

    def __init__(self, status: int, codigo: str, mensagem: str) -> None:
        """guarda status http, codigo e mensagem.

        Args:
            status: status http da resposta.
            codigo: identificador estavel do erro.
            mensagem: texto legivel para o estudante.
        """
        super().__init__(mensagem)
        self.status, self.erro = status, Erro(codigo=codigo, mensagem=mensagem)


def _resposta(
    status: int, erro: Erro, headers: dict[str, str] | None = None
) -> JSONResponse:
    corpo = RespostaErro(erro=erro).model_dump()
    return JSONResponse(corpo, status_code=status, headers=headers)


def registrar_erros(app: FastAPI) -> None:
    """coloca todo erro no formato {"erro": {"codigo", "mensagem"}}.

    chamar antes do cors, para o 500 ficar dentro dele.

    Args:
        app: aplicacao que recebe os handlers.
    """

    @app.exception_handler(ApiError)
    async def erro_api(_: Request, exc: ApiError) -> JSONResponse:
        return _resposta(exc.status, exc.erro)

    # rota inexistente, metodo errado etc.
    @app.exception_handler(HTTPException)
    async def erro_http(_: Request, exc: HTTPException) -> JSONResponse:
        erro = Erro(codigo=f"http_{exc.status_code}", mensagem=str(exc.detail))
        return _resposta(exc.status_code, erro, exc.headers)  # Allow, WWW-Authenticate

    @app.exception_handler(RequestValidationError)
    async def erro_validacao(_: Request, exc: RequestValidationError) -> JSONResponse:
        campos = ", ".join(".".join(map(str, e["loc"][1:])) for e in exc.errors())
        erro = Erro(codigo="dados_invalidos", mensagem=f"campos invalidos: {campos}")
        return _resposta(422, erro)

    # middleware e nao exception_handler(Exception): esse roda fora do cors e o
    # navegador bloqueia o 500. nunca vaza detalhe interno
    @app.middleware("http")
    async def erro_interno(
        request: Request, seguir: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        try:
            return await seguir(request)
        except Exception:
            logger.exception("erro inesperado em {}", request.url.path)
            mensagem = "erro inesperado, tente de novo"
            return _resposta(500, Erro(codigo="erro_interno", mensagem=mensagem))
