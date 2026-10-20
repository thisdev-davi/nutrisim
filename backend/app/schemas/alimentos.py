"""Contratos da API de alimentos."""

from pydantic import BaseModel


class ResultadoAlimento(BaseModel):
    """Alimento retornado pela busca."""

    id: int
    nome: str
    categoria_id: int
