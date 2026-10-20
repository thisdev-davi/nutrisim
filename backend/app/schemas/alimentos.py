"""Contratos da API de alimentos."""

from pydantic import BaseModel


class ResultadoAlimento(BaseModel):
    """Alimento retornado pela busca."""

    id: int
    nome: str
    categoria_id: int
    kcal: float | None
    proteina: float | None
    carboidratos: float | None
    lipidios: float | None
    fibra_alimentar: float | None
    sodio: float | None
    gordura_saturada: float | None
