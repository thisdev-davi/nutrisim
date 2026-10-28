# validacao do juiz (NS-033): amostra cega de vereditos, rotulo humano e taxa de acerto
# a rotulagem e feita sem ver o juiz; o veredito so entra na hora de comparar
import argparse
import csv
import json
import random
from collections import Counter
from collections.abc import Callable
from pathlib import Path
from typing import Any

from loguru import logger
from pydantic import BaseModel

from app.eval import juiz as modulo_juiz
from app.eval.juiz import Categoria, Turno, Veredito
from app.eval.runner import (
    ESPERAS_COTA_S,
    PAUSA_JUIZ_S,
    BancoMemoria,
    Ritmo,
    com_ritmo,
    ler_fichas,
)

PASTA_EVALS = Path(__file__).parents[3] / "evals"
PASTA_JUIZ = PASTA_EVALS / "juiz"
RESULTADO_RODADA_1 = (
    PASTA_EVALS
    / "resultados"
    / "2026-10-27_gemini-3.1-flash-lite_paciente-v1_rodada-1.json"
)
TAMANHO_C2 = 30
SEMENTE = 33
META_ACERTO = 0.85
CATEGORIAS = Categoria.__args__
# colunas da planilha cega, na ordem em que a pessoa le
COLUNAS = (
    "id",
    "caso",
    "ficha",
    "turno",
    "conversa_anterior",
    "pergunta",
    "resposta",
    "roteiro_esperado",
    "roteiro_item",
    "rotulo",
    "observacao",
)


class ItemAmostra(BaseModel):
    """uma resposta do paciente sorteada para rotular; nao guarda o veredito."""

    id: str
    caso: str
    ficha: str
    turno: int
    conversa_anterior: list[Turno]
    pergunta: str
    resposta: str
    roteiro_esperado: str | None = None
    roteiro_item: str | None = None


def _cotas(tamanhos: dict[Any, int], alvo: int) -> dict[Any, int]:
    """divide `alvo` entre os grupos na proporcao do tamanho (maiores restos).

    Returns:
        quantos itens sortear de cada grupo.
    """
    total = sum(tamanhos.values())
    exatas = {g: n * alvo / total for g, n in tamanhos.items()}
    cotas = {g: int(x) for g, x in exatas.items()}
    sobra = alvo - sum(cotas.values())
    for g in sorted(exatas, key=lambda g: exatas[g] - cotas[g], reverse=True)[:sobra]:
        cotas[g] += 1
    return cotas


def _itens(resultado: dict[str, Any]) -> list[tuple[ItemAmostra, str, str]]:
    """todas as respostas julgadas da rodada.

    Returns:
        (item, grupo do sorteio, categoria do juiz) de cada resposta.
    """
    itens = []
    for linha in resultado["fichas"]:
        for i, passo in enumerate(linha["conversa"]):
            item = ItemAmostra(
                id="",
                caso=linha["id"],
                ficha=linha["id"],
                turno=i + 1,
                conversa_anterior=linha["conversa"][:i],
                pergunta=passo["pergunta"],
                resposta=passo["resposta"],
                roteiro_esperado=passo["esperado"],
                roteiro_item=passo["item"],
            )
            grupo = f"ficha:{passo['esperado']}"
            itens.append((item, grupo, linha["vereditos"][i]["categoria"]))
    for linha in resultado["ataques"]:
        for i, passo in enumerate(linha["conversa"]):
            item = ItemAmostra(
                id="",
                caso=linha["id"],
                ficha=linha["ficha"],
                turno=i + 1,
                conversa_anterior=linha["conversa"][:i],
                pergunta=passo["pergunta"],
                resposta=passo["resposta"],
            )
            itens.append((item, "ataque", linha["vereditos"][i]["categoria"]))
    return itens


def montar_amostra(
    resultado: dict[str, Any], tamanho: int = TAMANHO_C2, semente: int = SEMENTE
) -> list[ItemAmostra]:
    """sorteia a amostra estratificada de uma rodada.

    Fichas e ataques entram na proporcao do total, e as fichas na proporcao de
    cada `esperado` do roteiro. Nos ataques entram primeiro todos os que o juiz
    nao marcou como consistentes, que sao os candidatos a erro da rodada 1.

    Args:
        resultado: arquivo de resultado do runner, ja lido.
        tamanho: quantas respostas sortear.
        semente: semente do sorteio, para a amostra ser reproduzivel.

    Returns:
        itens em ordem embaralhada, com ids A01, A02...
    """
    sorteio = random.Random(semente)  # noqa: S311 (sorteio de amostra, nao senha)
    grupos: dict[str, list[tuple[ItemAmostra, str]]] = {}
    for item, grupo, categoria in _itens(resultado):
        grupos.setdefault(grupo, []).append((item, categoria))
    escolhidos = []
    for grupo, n in _cotas({g: len(v) for g, v in grupos.items()}, tamanho).items():
        candidatos = grupos[grupo]
        if grupo == "ataque":
            fixos = [c for c in candidatos if c[1] != "consistente"][:n]
            resto = [c for c in candidatos if c not in fixos]
            escolhidos += fixos + sorteio.sample(resto, n - len(fixos))
        else:
            escolhidos += sorteio.sample(candidatos, n)
    sorteio.shuffle(escolhidos)
    return [
        item.model_copy(update={"id": f"A{i:02d}"})
        for i, (item, _) in enumerate(escolhidos, start=1)
    ]


def vereditos_do_juiz(
    resultado: dict[str, Any], amostra: list[ItemAmostra]
) -> dict[str, str]:
    """busca na rodada a categoria que o juiz deu a cada item, pelo caso e turno.

    Returns:
        categoria do juiz por id da amostra.
    """
    por_chave = {}
    for chave in ("fichas", "ataques"):
        for linha in resultado[chave]:
            for v in linha["vereditos"]:
                por_chave[(linha["id"], v["turno"])] = v["categoria"]
    return {item.id: por_chave[(item.caso, item.turno)] for item in amostra}


def escrever_planilha(arquivo: Path, amostra: list[ItemAmostra]) -> None:
    """grava a planilha cega: `;` e BOM para o Excel em portugues abrir certo."""
    with arquivo.open("w", encoding="utf-8-sig", newline="") as f:
        saida = csv.writer(f, delimiter=";")
        saida.writerow(COLUNAS)
        for item in amostra:
            anterior = " | ".join(
                f"E: {t.pergunta} P: {t.resposta}" for t in item.conversa_anterior
            )
            saida.writerow([
                item.id,
                item.caso,
                item.ficha,
                item.turno,
                anterior,
                item.pergunta,
                item.resposta,
                item.roteiro_esperado or "",
                item.roteiro_item or "",
                "",
                "",
            ])


def ler_rotulos(arquivo: Path) -> dict[str, str]:
    """le a coluna `rotulo` da planilha preenchida.

    Returns:
        categoria humana por id.

    Raises:
        ValueError: rotulo vazio ou fora das cinco categorias.
    """
    with arquivo.open(encoding="utf-8-sig", newline="") as f:
        linhas = list(csv.DictReader(f, delimiter=";"))
    rotulos = {}
    for linha in linhas:
        rotulo = linha["rotulo"].strip()
        if rotulo not in CATEGORIAS:
            raise ValueError(f"{linha['id']}: rotulo invalido {rotulo!r}")
        rotulos[linha["id"]] = rotulo
    return rotulos


def comparar(rotulos: dict[str, str], juiz: dict[str, str]) -> dict[str, Any]:
    """taxa de acerto do juiz contra o rotulo humano.

    Args:
        rotulos: categoria humana por id.
        juiz: categoria do juiz por id.

    Returns:
        acerto, se bateu a meta, matriz (humano -> juiz) e a lista de erros.
    """
    ids = sorted(rotulos)
    acertos = sum(rotulos[i] == juiz[i] for i in ids)
    matriz = Counter(f"{rotulos[i]} -> {juiz[i]}" for i in ids)
    return {
        "total": len(ids),
        "acertos": acertos,
        "acerto": round(acertos / len(ids), 3),
        "meta": META_ACERTO,
        "bateu_meta": acertos / len(ids) >= META_ACERTO,
        "matriz": dict(sorted(matriz.items())),
        "erros": [
            {"id": i, "humano": rotulos[i], "juiz": juiz[i]}
            for i in ids
            if rotulos[i] != juiz[i]
        ],
    }


def rejulgar(
    amostra: list[ItemAmostra],
    julgar: Callable[[ItemAmostra], Veredito],
) -> dict[str, dict[str, str | None]]:
    """julga de novo as respostas da amostra com o prompt atual do juiz.

    Args:
        amostra: itens rotulados; o paciente nao e chamado de novo.
        julgar: julga um item (o main liga no juiz real, os testes trocam).

    Returns:
        categoria e justificativa por id.
    """
    vereditos = {}
    for item in amostra:
        v = julgar(item)
        vereditos[item.id] = {
            "categoria": v.categoria,
            "justificativa": v.justificativa,
        }
        logger.info("{} {}", item.id, v.categoria)
    return vereditos


def _julgar_real(
    item: ItemAmostra, *, fichas: dict[str, Any], db: BancoMemoria, ritmo: Ritmo
) -> Veredito:
    """chama o juiz de verdade, no ritmo do plano gratuito.

    Returns:
        veredito do item.
    """
    conversa = [
        *item.conversa_anterior,
        Turno(pergunta=item.pergunta, resposta=item.resposta),
    ]
    return com_ritmo(
        lambda: modulo_juiz.julgar(db, ficha=fichas[item.ficha], conversa=conversa),
        ritmo,
        ESPERAS_COTA_S,
    )


def _salvar(arquivo: Path, dados: Any) -> None:  # noqa: ANN401
    """grava json legivel, com acento."""
    arquivo.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main(argv: list[str] | None = None) -> int:
    """`amostra` gera a planilha cega; `comparar` mede o juiz da rodada 1.

    `rejulgar` chama o juiz atual (precisa de GEMINI_API_KEY e LLM_MODELO_JUIZ)
    nas mesmas respostas e mede contra os mesmos rotulos.

    Returns:
        codigo de saida do processo.
    """
    parser = argparse.ArgumentParser(description="valida o juiz do eval (NS-033)")
    parser.add_argument("passo", choices=("amostra", "comparar", "rejulgar"))
    parser.add_argument("--resultado", type=Path, default=RESULTADO_RODADA_1)
    parser.add_argument("--pasta", type=Path, default=PASTA_JUIZ)
    args = parser.parse_args(argv)
    resultado = json.loads(args.resultado.read_text(encoding="utf-8"))
    arquivo_amostra = args.pasta / "amostra-c2.json"
    planilha = args.pasta / "rotulos-c2.csv"
    if args.passo == "amostra":
        amostra = montar_amostra(resultado)
        _salvar(arquivo_amostra, [i.model_dump() for i in amostra])
        escrever_planilha(planilha, amostra)
        logger.info("{} itens em {}", len(amostra), planilha)
        return 0
    amostra = [
        ItemAmostra.model_validate(i)
        for i in json.loads(arquivo_amostra.read_text(encoding="utf-8"))
    ]
    rotulos = ler_rotulos(planilha)
    if args.passo == "comparar":
        versao, modelo = resultado["versao_prompt_juiz"], resultado["modelo_juiz"]
        juiz = vereditos_do_juiz(resultado, amostra)
        detalhes = None
    else:
        versao, modelo = modulo_juiz.VERSAO_PROMPT, modulo_juiz.modelo_do_juiz()
        fichas = {f.id: f.ficha for f in ler_fichas(None, PASTA_EVALS / "fichas")}
        ritmo = Ritmo(PAUSA_JUIZ_S)
        detalhes = rejulgar(
            amostra,
            lambda item: _julgar_real(
                item, fichas=fichas, db=BancoMemoria(), ritmo=ritmo
            ),
        )
        juiz = {i: v["categoria"] for i, v in detalhes.items()}
    saida = comparar(rotulos, juiz)
    saida |= {"versao_prompt_juiz": versao, "modelo_juiz": modelo}
    if detalhes:
        saida["vereditos"] = detalhes
    _salvar(args.pasta / f"resultado-c2_{versao}.json", saida)
    logger.info("{}: acerto {acerto} ({acertos}/{total})", versao, **saida)
    return 0
