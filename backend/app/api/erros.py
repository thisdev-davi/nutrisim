from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
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


def _resposta(status: int, erro: Erro) -> JSONResponse:
    return JSONResponse(RespostaErro(erro=erro).model_dump(), status_code=status)


def registrar_erros(app: FastAPI) -> None:
    """coloca todo erro no formato {"erro": {"codigo", "mensagem"}}.

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
        return _resposta(exc.status_code, erro)

    @app.exception_handler(RequestValidationError)
    async def erro_validacao(_: Request, exc: RequestValidationError) -> JSONResponse:
        campos = ", ".join(".".join(map(str, e["loc"][1:])) for e in exc.errors())
        erro = Erro(codigo="dados_invalidos", mensagem=f"campos invalidos: {campos}")
        return _resposta(422, erro)

    # nunca vaza detalhe interno
    @app.exception_handler(Exception)
    async def erro_interno(_: Request, __: Exception) -> JSONResponse:
        erro = Erro(codigo="erro_interno", mensagem="erro inesperado, tente de novo")
        return _resposta(500, erro)
