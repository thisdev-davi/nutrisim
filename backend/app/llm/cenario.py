# etapa 4: cenarios ideal e realista (NS-046)
# o llm estima so a adesao e as trocas; composicao, adequacao e peso saem do motor
import json
import os
import time
from pathlib import Path
from typing import Any
from uuid import UUID

# sem alias publico no sdk 2.x para os erros da api de interactions
from google.genai._gaos.lib.compat_errors import (  # noqa: PLC2701
    APIConnectionError,
    InternalServerError,
    RateLimitError,
)
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.alimentos import buscar_alimentos
from app.db import modelos
from app.llm import cliente
from app.motor.adequacao import calcular_adequacao
from app.motor.composicao import NUTRIENTES, Item, calcular_refeicao
from app.motor.projecao import AVISO, projetar_peso
from app.schemas.api import (
    AdequacaoNutriente,
    AdesaoRefeicao,
    Cenario,
    CenarioRealista,
    Cenarios,
    NovoPlano,
    PontoSemana,
    Substituicao,
)
from app.schemas.ficha import FichaPaciente

PROMPT = Path(__file__).with_name("prompts") / "cenario-v1.md"
BUSCAS = 6  # rodadas de ferramenta por tentativa: segura um llm que so busca
# segundos: por chamada e para a geracao inteira, que roda com o estudante esperando
TIMEOUT_CHAMADA, PRAZO = 30, 60
FERRAMENTA = {
    "type": "function",
    "name": "buscar_alimentos",
    "description": "busca alimentos da tabela TACO pelo nome; devolve id e nome",
    "parameters": {
        "type": "object",
        "properties": {"nome": {"type": "string", "description": "ex.: macarrao"}},
        "required": ["nome"],
    },
}


class Troca(BaseModel):
    """troca que o llm escolheu; os nomes vem da TACO, nao dele."""

    refeicao: str
    original_id: int
    substituto_id: int
    motivo: str


class Estimativa(BaseModel):
    """saida do llm: so adesao e trocas, nenhum numero fisiologico."""

    adesao: list[AdesaoRefeicao]
    trocas: list[Troca]


# id -> (nome, nutrientes por 100 g)
Taco = dict[int, tuple[str, dict[str, float | None]]]


def carregar_taco(db: Session, ids: set[int]) -> Taco:
    """nome e nutrientes dos alimentos, para o motor.

    Args:
        db: sessao do banco.
        ids: ids da TACO.

    Returns:
        id -> (nome, nutrientes por 100 g); sem linha de nutrientes vira NA.
    """
    linhas = db.execute(
        select(modelos.Alimentos.id, modelos.Alimentos.nome, modelos.Nutrientes)
        .outerjoin(modelos.Nutrientes, modelos.Nutrientes.id == modelos.Alimentos.id)
        .where(modelos.Alimentos.id.in_(ids))
    )
    return {
        id_: (nome, {n: getattr(nutrientes, n, None) for n in NUTRIENTES})
        for id_, nome, nutrientes in linhas
    }


def buscar_taco(db: Session, nome: str) -> list[dict[str, Any]]:
    """ferramenta do llm: so id e nome, os numeros ficam com o motor.

    Args:
        db: sessao do banco.
        nome: termo de busca.

    Returns:
        ate 20 alimentos.
    """
    achados = buscar_alimentos(db, nome[:100])[:20]
    return [{"id": a.id, "nome": a.nome} for a in achados]


def _chamar(
    db: Session,
    historico: list,
    tentativa: int,
    sessao_id: UUID | None,
    prazo: float,
) -> Any:  # noqa: ANN401
    """uma chamada ao gemini com a ferramenta, com os tokens registrados.

    Returns:
        interacao devolvida pelo provedor.

    Raises:
        LLMIndisponivelError: falha passageira do provedor ou prazo esgotado.
    """
    modelo = os.environ["LLM_MODELO"]
    restante = prazo - time.monotonic()
    if restante <= 0:
        raise cliente.LLMIndisponivelError("cenario: prazo esgotado")
    try:
        resposta = cliente._cliente().interactions.create(  # noqa: SLF001
            model=modelo,
            timeout=min(TIMEOUT_CHAMADA, restante),
            input=list(historico),
            system_instruction=PROMPT.read_text(encoding="utf-8"),
            store=False,  # sem historico no provedor: ele volta inteiro a cada rodada
            tools=[FERRAMENTA],
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": Estimativa.model_json_schema(),
            },
        )
    # 4xx fica de fora de proposito: e bug nosso, nao sobrecarga; o timeout
    # (APITimeoutError) e um APIConnectionError
    except (InternalServerError, RateLimitError, APIConnectionError) as e:
        raise cliente.LLMIndisponivelError("cenario: provedor indisponivel") from e
    # ponytail: repete o registro do cliente.gerar; extrair registrar_uso no
    # cliente.py quando outra tarefa usar ferramentas
    uso = resposta.usage
    db.add(
        modelos.ChamadaLLM(
            sessao_id=sessao_id,
            tarefa="cenario",
            modelo=modelo,
            tentativa=tentativa,
            tokens_entrada=getattr(uso, "total_input_tokens", None) or 0,
            tokens_saida=sum(
                getattr(uso, campo, None) or 0
                for campo in ("total_output_tokens", "total_thought_tokens")
            ),
        )
    )
    return resposta


def _conferir(estimativa: Estimativa, plano: NovoPlano, vistos: set[int]) -> None:
    """regras de coerencia que o schema nao pega.

    Raises:
        ValueError: refeicao faltando ou a mais, adesao zero no dia todo, troca
            repetida, de item fora da refeicao ou com substituto que a busca
            nao devolveu (inventado).
    """
    nomes = sorted(r.nome for r in plano.refeicoes)
    if sorted(a.refeicao for a in estimativa.adesao) != nomes:
        raise ValueError("adesao precisa de uma entrada por refeicao do plano")
    # ninguem deixa de comer o dia todo; e saida quebrada, nao estimativa
    if all(a.adesao == 0 for a in estimativa.adesao):
        raise ValueError("adesao zero em todas as refeicoes")
    pares = [(t.refeicao, t.original_id) for t in estimativa.trocas]
    if len(pares) != len(set(pares)):
        raise ValueError("troca repetida para o mesmo item")
    itens = {r.nome: {i.alimento_id for i in r.itens} for r in plano.refeicoes}
    for t in estimativa.trocas:
        if t.original_id not in itens.get(t.refeicao, set()):
            raise ValueError(f"troca de item fora da refeicao: {t}")
        if t.substituto_id not in vistos:
            raise ValueError(f"substituto fora da busca: {t}")


def estimar(
    db: Session,
    paciente: FichaPaciente,
    plano: NovoPlano,
    taco: Taco,
    sessao_id: UUID | None = None,
) -> Estimativa:
    """adesao por refeicao e trocas, com a busca na TACO por function calling.

    Cada tentativa recomeca a conversa; saida fora do schema ou incoerente
    gera outra tentativa, como no cliente.gerar.

    Args:
        db: sessao do banco, para os tokens e a busca.
        paciente: o que o paciente sabe sobre si.
        plano: plano encerrado.
        taco: nomes dos alimentos do plano.
        sessao_id: sessao do estudante.

    Returns:
        estimativa conferida.

    Raises:
        SaidaInvalidaError: nenhuma tentativa passou.
    """
    entrada = json.dumps(
        {
            "paciente": paciente.model_dump(),
            "plano": [
                {
                    "refeicao": r.nome,
                    "itens": [
                        {
                            "id": i.alimento_id,
                            "nome": taco[i.alimento_id][0],
                            "gramas": i.gramas,
                        }
                        for i in r.itens
                    ],
                }
                for r in plano.refeicoes
            ],
        },
        ensure_ascii=False,
    )
    erro: ValueError | None = None
    prazo = time.monotonic() + PRAZO
    for tentativa in range(1, cliente.TENTATIVAS + 1):
        historico: list = [
            {"type": "user_input", "content": [{"type": "text", "text": entrada}]}
        ]
        vistos: set[int] = set()
        for _ in range(BUSCAS):
            resposta = _chamar(db, historico, tentativa, sessao_id, prazo)
            passos = resposta.steps or []
            pedidos = [p for p in passos if p.type == "function_call"]
            if not pedidos:
                break
            # devolve os passos do modelo (com a assinatura do raciocinio)
            historico += [
                p.model_dump(mode="json", by_alias=True, exclude_none=True)
                for p in passos
                if p.type != "user_input"
            ]
            for pedido in pedidos:
                argumentos = pedido.arguments or {}
                achados = buscar_taco(db, str(argumentos.get("nome", "")))
                vistos |= {a["id"] for a in achados}
                historico.append({
                    "type": "function_result",
                    "call_id": pedido.id,
                    "name": pedido.name,
                    "result": json.dumps(achados, ensure_ascii=False),
                })
        else:
            logger.warning("cenario: tentativa {} so buscou, sem resposta", tentativa)
        try:  # ValidationError do pydantic tambem e ValueError
            estimativa = Estimativa.model_validate_json(resposta.output_text or "")
            _conferir(estimativa, plano, vistos)
        except ValueError as e:
            logger.warning("cenario: tentativa {} invalida: {}", tentativa, e)
            erro = e
            continue
        return estimativa
    raise cliente.SaidaInvalidaError(
        f"cenario: saida invalida em {cliente.TENTATIVAS} tentativas"
    ) from erro


def _cenario(
    paciente: FichaPaciente, taco: Taco, consumo: list[tuple[int, float]]
) -> dict[str, Any]:
    """peso e adequacao do consumo medio, tudo pelo motor.

    Returns:
        campos comuns de Cenario.
    """
    total = calcular_refeicao([Item(taco[i][0], g, taco[i][1]) for i, g in consumo])
    adequacao = {
        n: AdequacaoNutriente(
            consumo=a.consumo,
            referencia=a.referencia.valor,
            percentual=a.percentual,
            classificacao=a.classificacao,
            sem_dado=a.sem_dado,
        )
        for n, a in calcular_adequacao(total, paciente.genero, paciente.idade).items()
    }
    pesos = projetar_peso(
        paciente.genero,
        paciente.idade,
        paciente.peso_kg,
        paciente.altura_cm,
        paciente.atividade_fisica,
        total.valores["kcal"],
    )
    peso = [PontoSemana(semana=s, peso_kg=p) for s, p in enumerate(pesos)]
    return {"peso": peso, "adequacao": adequacao}


def gerar_cenarios(db: Session, sessao: modelos.Sessao) -> Cenarios:
    """cenario ideal (o plano inteiro) e realista (adesao e trocas do llm).

    Args:
        db: sessao do banco.
        sessao: sessao com o plano encerrado.

    Returns:
        os dois cenarios e o aviso da projecao.
    """
    plano = NovoPlano.model_validate(sessao.plano)
    paciente = FichaPaciente.model_validate(sessao.ficha["paciente"])
    taco = carregar_taco(db, {i.alimento_id for r in plano.refeicoes for i in r.itens})
    estimativa = estimar(db, paciente, plano, taco, sessao.id)
    taco |= carregar_taco(db, {t.substituto_id for t in estimativa.trocas})

    adesao = {a.refeicao: a.adesao for a in estimativa.adesao}
    trocas = {(t.refeicao, t.original_id): t.substituto_id for t in estimativa.trocas}
    # ponytail: o substituto entra com as mesmas gramas do original
    ideal, realista = [], []
    for r in plano.refeicoes:
        for i in r.itens:
            ideal.append((i.alimento_id, i.gramas))
            id_ = trocas.get((r.nome, i.alimento_id), i.alimento_id)
            realista.append((id_, i.gramas * adesao[r.nome]))

    substituicoes = [
        Substituicao(
            refeicao=t.refeicao,
            original_id=t.original_id,
            original=taco[t.original_id][0],
            substituto_id=t.substituto_id,
            substituto=taco[t.substituto_id][0],
            motivo=t.motivo,
        )
        for t in estimativa.trocas
    ]
    return Cenarios(
        ideal=Cenario(**_cenario(paciente, taco, ideal)),
        realista=CenarioRealista(
            **_cenario(paciente, taco, realista),
            adesao=estimativa.adesao,
            substituicoes=substituicoes,
        ),
        aviso=AVISO,
    )
