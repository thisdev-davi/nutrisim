# etapa 1: escolha do perfil e criacao da sessao
# mock: dados fixos ate a NS-019 gerar o caso de verdade
from fastapi import APIRouter

from app.api.erros import ApiError
from app.schemas.api import (
    Dificuldade,
    Etapa,
    NovaSessao,
    Opcoes,
    Paciente,
    Perfil,
    RespostaErro,
    Sessao,
)

router = APIRouter(tags=["etapa 1: caso"], responses={422: {"model": RespostaErro}})

# perfil provisorio ate a NS-015 fechar a lista
PERFIS = [
    Perfil(
        id="adulto-hipertensao",
        nome="Adulto com hipertensao",
        descricao="adulto de 40 a 60 anos com pressao alta e excesso de peso",
    )
]

SESSAO_MOCK = Sessao(
    id="mock",
    etapa=Etapa.ANAMNESE,
    perfil_id="adulto-hipertensao",
    dificuldade=Dificuldade.MEDIO,
    paciente=Paciente(
        nome="Carlos",
        idade=52,
        queixa_principal="pressao alta e dificuldade para perder peso",
    ),
    mensagens=[],
)


@router.get("/perfis")
async def listar_opcoes() -> Opcoes:
    """perfis e dificuldades para a tela de selecao.

    Returns:
        perfis e niveis disponiveis.
    """
    return Opcoes(perfis=PERFIS, dificuldades=list(Dificuldade))


@router.post("/sessoes", status_code=201)
async def criar_sessao(dados: NovaSessao) -> Sessao:
    """cria o caso e a sessao; a ficha oculta fica so no backend.

    Args:
        dados: perfil e dificuldade escolhidos.

    Returns:
        sessao criada, ja na etapa de anamnese.

    Raises:
        ApiError: perfil inexistente.
    """
    if dados.perfil_id not in {p.id for p in PERFIS}:
        raise ApiError(422, "perfil_invalido", "perfil nao encontrado")
    return SESSAO_MOCK.model_copy(update=dados.model_dump())
