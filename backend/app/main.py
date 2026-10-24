import os

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer

from app.api import alimentos, anamnese, caso
from app.api.erros import registrar_erros

app = FastAPI(title="NutriSim")
registrar_erros(app)

# libera so o front configurado (vazio cai no padrao)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("FRONTEND_URL") or "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# token bearer so declarado; a NS-035 passa a exigir
bearer = Depends(HTTPBearer(auto_error=False))
for rotas in (alimentos.router, caso.router, anamnese.router):
    app.include_router(rotas, prefix="/api", dependencies=[bearer])


@app.get("/health")
async def health() -> dict[str, str]:
    """indica que a api esta no ar.

    Returns:
        status fixo "online".
    """
    return {"status": "online"}
