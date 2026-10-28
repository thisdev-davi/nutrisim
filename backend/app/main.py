import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import alimentos, anamnese, auth, caso
from app.api.erros import registrar_erros
from app.schemas.api import RespostaErro
from app.seguranca import segredo


@asynccontextmanager
async def ciclo_de_vida(_app: FastAPI) -> AsyncGenerator[None, None]:
    """confere a configuracao antes de aceitar requisicoes.

    Sem isso, a falta do JWT_SEGREDO so aparecia como 500 no meio do cadastro.

    Yields:
        controle para a aplicacao rodar.
    """
    segredo()  # chave ausente ou curta impede a api de subir
    yield


app = FastAPI(title="NutriSim", lifespan=ciclo_de_vida)
registrar_erros(app)

# libera so o front configurado (vazio cai no padrao)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("FRONTEND_URL") or "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# cadastro e login abertos; toda rota da simulacao exige o token (NS-035)
app.include_router(auth.router, prefix="/api")
protegida = Depends(auth.usuario_atual)
for rotas in (alimentos.router, caso.router, anamnese.router):
    app.include_router(
        rotas,
        prefix="/api",
        dependencies=[protegida],
        responses={401: {"model": RespostaErro}},
    )


@app.get("/health")
async def health() -> dict[str, str]:
    """indica que a api esta no ar.

    Returns:
        status fixo "online".
    """
    return {"status": "online"}
