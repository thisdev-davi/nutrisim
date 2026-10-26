# etapa 1: escolha do perfil e criacao da sessao (NS-019)
import json
import random
from pathlib import Path
from typing import Annotated, get_args
from uuid import uuid4

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.erros import ApiError
from app.db import modelos
from app.db.deps import obter_sessao
from app.llm.cliente import LLMIndisponivelError, SaidaInvalidaError, gerar
from app.motor.energia import Sexo
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
from app.schemas.ficha import Ficha, Restricoes

router = APIRouter(
    tags=["etapa 1: caso"],
    responses={422: {"model": RespostaErro}, 503: {"model": RespostaErro}},
)

PROMPT = Path(__file__).parents[1] / "llm" / "prompts" / "caso-v1.md"

# perfis do content/perfis.md (NS-015); a descricao nao revela a conduta esperada
PERFIS = [
    Perfil(
        id="adulto-hipertensao",
        nome="Adulto com hipertensão",
        descricao="Adulto de 40 a 60 anos com pressão alta.",
    ),
    Perfil(
        id="adulto-diabetes-tipo2",
        nome="Adulto com diabetes tipo 2",
        descricao="Adulto de 40 a 65 anos com diabetes tipo 2.",
    ),
    Perfil(
        id="adulto-dislipidemia",
        nome="Adulto com colesterol alto",
        descricao="Adulto de 30 a 60 anos com colesterol LDL elevado.",
    ),
    Perfil(
        id="idoso-baixa-ingestao",
        nome="Pessoa idosa com perda de apetite",
        descricao="Pessoa de 65 a 80 anos que está comendo pouco.",
    ),
    Perfil(
        id="adulto-jovem-emagrecimento",
        nome="Adulto jovem que quer emagrecer",
        descricao="Adulto de 18 a 30 anos que pede uma dieta para emagrecer.",
    ),
]

# numeros do content/perfis.md: o motor confere o plano com eles, entao nao
# ficam a criterio do llm
RESTRICOES = {
    "adulto-hipertensao": {"sodio_max_mg": 2000},
    "adulto-diabetes-tipo2": {"fibras_min_g_por_1000kcal": 14},
    "adulto-dislipidemia": {"gordura_saturada_max_pct_vet": 10},
    "idoso-baixa-ingestao": {"proteina_g_kg_min": 1.2, "proteina_g_kg_max": 1.5},
}

# sorteados no codigo para a variedade nao depender do llm
SORTEIO = {
    "genero": get_args(Sexo),
    "renda": ["baixa", "media", "alta"],
    "rotina": [
        "horario comercial",
        "turno noturno",
        "trabalho braçal",
        "home office",
        "aposentadoria",
        "cuidado de familiar (dupla jornada)",
    ],
}


def para_api(linha: modelos.Sessao) -> Sessao:
    """so o que o estudante pode ver da sessao.

    Args:
        linha: sessao do banco, com a ficha oculta.

    Returns:
        sessao sem a ficha.
    """
    return Sessao(
        id=str(linha.id),
        etapa=linha.etapa,
        perfil_id=linha.perfil_id,
        dificuldade=linha.dificuldade,
        # extra e ignorado: so passam nome, idade e queixa
        paciente=Paciente.model_validate(linha.ficha["paciente"]),
        mensagens=[],  # a NS-020 grava o historico
    )


@router.get("/perfis")
async def listar_opcoes() -> Opcoes:
    """perfis e dificuldades para a tela de selecao.

    Returns:
        perfis e niveis disponiveis.
    """
    return Opcoes(perfis=PERFIS, dificuldades=list(Dificuldade))


def gerar_ficha(db: Session, dados: NovaSessao) -> Ficha:
    """pede a ficha ao llm e impoe o que vem do perfil, nao do llm.

    Args:
        db: sessao do banco, para o registro de tokens.
        dados: perfil e dificuldade escolhidos.

    Returns:
        ficha validada.
    """
    sorteio = {k: random.choice(v) for k, v in SORTEIO.items()}  # noqa: S311
    # ponytail: sem sessao_id porque a sessao ainda nao existe (fk); ligar
    # depois do insert se o custo por sessao precisar
    ficha = gerar(
        db,
        tarefa="caso",
        schema=Ficha,
        entrada=json.dumps(dados.model_dump() | sorteio, ensure_ascii=False),
        instrucao=PROMPT.read_text(),
    )
    emagrecimento = dados.perfil_id == "adulto-jovem-emagrecimento"
    conduta = "encaminhamento" if emagrecimento else "plano"
    gabarito = ficha.gabarito.model_copy(update={"conduta_esperada": conduta})
    restricoes = Restricoes(
        **RESTRICOES.get(dados.perfil_id, {}),
        alimentos_evitados=ficha.restricoes.alimentos_evitados,
    )
    return ficha.model_copy(
        update=dados.model_dump() | {"gabarito": gabarito, "restricoes": restricoes}
    )


# def e nao async: o gerar bloqueia, entao roda no threadpool
@router.post("/sessoes", status_code=201)
def criar_sessao(
    dados: NovaSessao, db: Annotated[Session, Depends(obter_sessao)]
) -> Sessao:
    """cria o caso e a sessao; a ficha oculta fica so no backend.

    Args:
        dados: perfil e dificuldade escolhidos.
        db: sessao do banco.

    Returns:
        sessao criada, ja na etapa de anamnese.

    Raises:
        ApiError: perfil inexistente, llm sem saida valida ou fora do ar.
    """
    if dados.perfil_id not in {p.id for p in PERFIS}:
        raise ApiError(422, "perfil_invalido", "perfil nao encontrado")
    try:
        ficha = gerar_ficha(db, dados)
    except (SaidaInvalidaError, LLMIndisponivelError) as e:
        db.commit()  # guarda os tokens gastos nas tentativas
        raise ApiError(
            503, "caso_nao_gerado", "nao foi possivel gerar o caso, tente de novo"
        ) from e
    linha = modelos.Sessao(
        id=uuid4(),  # o default do modelo so roda no flush
        perfil_id=dados.perfil_id,
        dificuldade=dados.dificuldade,
        etapa=Etapa.ANAMNESE,
        ficha=ficha.model_dump(mode="json"),
    )
    db.add(linha)
    db.commit()
    return para_api(linha)
