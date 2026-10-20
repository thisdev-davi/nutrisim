"""Rotas de consulta dos alimentos."""

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

CARACTERES_COM_ACENTO = "áàâãäéèêëíìîïóòôõöúùûüç"
CARACTERES_SEM_ACENTO = "aaaaaeeeeiiiiooooouuuuc"


def normalizar_busca(texto: str) -> str:
    """Converte texto para comparação sem acentos e sem maiúsculas.

    Returns:
        Texto normalizado e sem espaços nas extremidades.
    """
    texto = texto.strip()
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(
        caractere for caractere in texto if not unicodedata.combining(caractere)
    ).lower()


def expressao_nome_normalizado():
    """Cria a expressão PostgreSQL para normalizar nomes na consulta.

    Returns:
        Expressão SQL com nomes em minúsculas e sem acentos.
    """
    return func.translate(
        func.lower(Alimentos.nome),
        CARACTERES_COM_ACENTO,
        CARACTERES_SEM_ACENTO,
    )


@router.get("/alimentos", response_model=list[ResultadoAlimento])
def buscar_alimentos(
    sessao: SessaoBanco,
    nome: Annotated[str, Query(min_length=1, max_length=100)],
) -> list[ResultadoAlimento]:
    """Busca alimentos por nome, ignorando acentos e maiúsculas.

    Returns:
        Até 50 alimentos que correspondem ao termo informado.
    """
    termo = normalizar_busca(nome)
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
        .where(expressao_nome_normalizado().contains(termo))
        .order_by(Alimentos.nome)
        .limit(50)
    )
    alimentos = sessao.execute(consulta).all()
    return [
        ResultadoAlimento(
            id=alimento.id,
            nome=alimento.nome,
            categoria_id=alimento.categoria_id,
            kcal=alimento.kcal,
            proteina=alimento.proteina,
            carboidratos=alimento.carboidratos,
            lipidios=alimento.lipidios,
            fibra_alimentar=alimento.fibra_alimentar,
            sodio=alimento.sodio,
            gordura_saturada=alimento.gordura_saturada,
        )
        for alimento in alimentos
    ]
