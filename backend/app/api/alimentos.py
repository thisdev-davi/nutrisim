"""rotas de consulta dos alimentos."""

import unicodedata
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.deps import obter_sessao
from app.db.modelos import AcidosGraxos, Alimentos, Nutrientes
from app.schemas.alimentos import ResultadoAlimento

router = APIRouter(tags=["alimentos"])
SessaoBanco = Annotated[Session, Depends(obter_sessao)]


def normalizar_busca(texto: str) -> str:
    """deixa o termo sem acento, em minusculo e com espaco simples.

    Returns:
        termo normalizado.
    """
    texto = unicodedata.normalize("NFKD", " ".join(texto.split()))
    return "".join(
        caractere for caractere in texto if not unicodedata.combining(caractere)
    ).lower()


@router.get("/alimentos", response_model=list[ResultadoAlimento])
def buscar_alimentos(
    sessao: SessaoBanco,
    nome: Annotated[str, Query(min_length=1, max_length=100)],
) -> list[ResultadoAlimento]:
    """busca alimentos por nome, ignorando acento e maiuscula.

    Returns:
        ate 50 alimentos que contem o termo.
    """
    termo = normalizar_busca(nome)
    if not termo:
        return []
    nome_normalizado = func.lower(func.unaccent(Alimentos.nome))

    consulta = (
        select(
            Alimentos.id,
            Alimentos.nome,
            Alimentos.category_id.label("categoria_id"),
            Nutrientes.kcal,
            Nutrientes.proteina,
            Nutrientes.carboidratos,
            Nutrientes.lipidios,
            Nutrientes.fibra_alimentar,
            Nutrientes.sodio,
            AcidosGraxos.gordura_saturada,
        )
        .outerjoin(Nutrientes, Nutrientes.id == Alimentos.id)
        .outerjoin(AcidosGraxos, AcidosGraxos.id == Alimentos.id)
        .where(nome_normalizado.contains(termo, autoescape=True))
        .order_by(Alimentos.nome)
        .limit(50)
    )
    return [
        ResultadoAlimento.model_validate(linha, from_attributes=True)
        for linha in sessao.execute(consulta).all()
    ]
