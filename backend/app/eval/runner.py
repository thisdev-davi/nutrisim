# runner do eval (NS-026): roda o roteiro de cada ficha contra o paciente e o juiz
# importa os servicos do backend em vez de chamar a api (decisao em evals/README.md)
import argparse
import json
import os
import time
from collections.abc import Callable
from datetime import date
from functools import partial
from pathlib import Path
from typing import Any, TypeVar

from loguru import logger

from app.db.modelos import ChamadaLLM
from app.eval import juiz
from app.eval.paciente import FichaEval, Paciente, PacienteFalso, PacienteReal
from app.llm.cliente import LLMIndisponivelError, SaidaInvalidaError

PASTA_EVALS = Path(__file__).parents[3] / "evals"
# plano gratuito: paciente 5/min e juiz 15/min; 20% de folga, retentativas contam
PAUSA_PACIENTE_S = 60 / 4
PAUSA_JUIZ_S = 60 / 12
ESPERAS_COTA_S = (30, 60, 120)
INCONSISTENTES = {"contradicao", "invencao_relevante"}

T = TypeVar("T")


class CotaEsgotadaError(Exception):
    """o provedor seguiu falhando depois de todas as esperas."""


class BancoMemoria(list):
    """no lugar do banco: guarda as chamadas ao llm para somar os tokens."""

    add = list.append


class Ritmo:
    """garante um intervalo minimo entre chamadas do mesmo modelo."""

    def __init__(
        self,
        intervalo_s: float,
        dormir: Callable[[float], None] = time.sleep,
        relogio: Callable[[], float] = time.monotonic,
    ) -> None:
        """comeca sem chamada anterior.

        Args:
            intervalo_s: segundos entre o inicio de duas chamadas.
            dormir: funcao de espera (os testes trocam).
            relogio: relogio monotonico (os testes trocam).
        """
        self.intervalo_s, self.dormir, self.relogio = intervalo_s, dormir, relogio
        self.ultima: float | None = None

    def esperar(self) -> None:
        """dorme o que falta para completar o intervalo desde a ultima chamada."""
        if self.ultima is not None:
            falta = self.ultima + self.intervalo_s - self.relogio()
            if falta > 0:
                self.dormir(falta)
        self.ultima = self.relogio()


def com_ritmo(
    acao: Callable[[], T], ritmo: Ritmo, esperas_cota: tuple[float, ...]
) -> T:
    """chama respeitando o ritmo e tenta de novo em erro de cota ou de rede.

    Args:
        acao: chamada ao llm.
        ritmo: ritmo do modelo chamado.
        esperas_cota: segundos de espera antes de cada nova tentativa.

    Returns:
        o que a acao devolver.

    Raises:
        CotaEsgotadaError: falhou em todas as tentativas.
    """
    for espera in esperas_cota:
        ritmo.esperar()
        try:
            return acao()
        except LLMIndisponivelError as e:
            logger.warning("{}; nova tentativa em {} s", e, espera)
            ritmo.dormir(espera)
    ritmo.esperar()
    try:
        return acao()
    except LLMIndisponivelError as e:
        raise CotaEsgotadaError(str(e)) from e


def rodar_ficha(  # noqa: PLR0913
    ficha: FichaEval,
    paciente: Paciente,
    execucao: int,
    *,
    db: BancoMemoria,
    ritmos: tuple[Ritmo, Ritmo],
    esperas_cota: tuple[float, ...] = ESPERAS_COTA_S,
) -> dict[str, Any]:
    """faz as perguntas do roteiro e julga cada resposta.

    Args:
        ficha: ficha de eval.
        paciente: paciente que responde.
        execucao: numero da execucao do caso (1 a 3).
        db: onde o cliente do llm registra os tokens.
        ritmos: ritmo do paciente e do juiz, nessa ordem.
        esperas_cota: esperas entre tentativas em erro de cota.

    Returns:
        linha de `fichas` no arquivo de resultado, com a conversa.
    """
    ritmo_paciente, ritmo_juiz = ritmos
    conversa: list[juiz.Turno] = []
    vereditos: list[juiz.Veredito] = []
    linha: dict[str, Any] = {"id": ficha.id, "execucao": execucao}
    for passo in ficha.roteiro:
        try:
            resposta = com_ritmo(
                lambda p=passo: paciente.responder(conversa, p.pergunta),
                ritmo_paciente,
                esperas_cota,
            )
        except SaidaInvalidaError:
            # sem resposta nao ha o que julgar; o resto do roteiro perde o sentido
            linha["falha"] = "paciente_saida_invalida"
            break
        conversa.append(juiz.Turno(pergunta=passo.pergunta, resposta=resposta))
        vereditos.append(
            com_ritmo(
                lambda: juiz.julgar(db, ficha=ficha.ficha, conversa=conversa),
                ritmo_juiz,
                esperas_cota,
            )
        )
    linha["conversa"] = [
        {**t.model_dump(), "esperado": p.esperado, "item": p.item}
        for t, p in zip(conversa, ficha.roteiro, strict=False)
    ]
    linha["vereditos"] = [v.model_dump() for v in vereditos]
    return linha


def metricas(fichas: list[dict[str, Any]]) -> dict[str, Any]:
    """taxa de inconsistencia media por execucao (evals/README.md).

    Args:
        fichas: linhas de `fichas` do resultado.

    Returns:
        metricas do resultado; None quando nao ha vereditos validos.
    """
    taxas, falhas = [], 0
    por_execucao: dict[int, list[str]] = {}
    for linha in fichas:
        for v in linha["vereditos"]:
            if v["falha"]:
                falhas += 1
            else:
                por_execucao.setdefault(linha["execucao"], []).append(v["categoria"])
    for categorias in por_execucao.values():
        ruins = sum(c in INCONSISTENTES for c in categorias)
        taxas.append(ruins / len(categorias))
    media = round(sum(taxas) / len(taxas), 4) if taxas else None
    return {"taxa_inconsistencia": media, "vereditos_com_falha": falhas}


def uso(db: BancoMemoria) -> dict[str, dict[str, int]]:
    """chamadas e tokens por tarefa, para acompanhar a cota.

    Args:
        db: chamadas registradas pelo cliente do llm.

    Returns:
        totais por tarefa.
    """
    total: dict[str, dict[str, int]] = {}
    for c in db:
        if isinstance(c, ChamadaLLM):
            t = total.setdefault(
                c.tarefa, {"chamadas": 0, "tokens_entrada": 0, "tokens_saida": 0}
            )
            t["chamadas"] += 1
            t["tokens_entrada"] += c.tokens_entrada
            t["tokens_saida"] += c.tokens_saida
    return total


def caminho_resultado(pasta: Path, dia: date, modelo: str, versao: str) -> Path:
    """resultados/AAAA-MM-DD_<modelo>_<versao-prompt>.json.

    Args:
        pasta: pasta dos resultados.
        dia: data da rodada.
        modelo: modelo do paciente.
        versao: versao do prompt do paciente.

    Returns:
        caminho do arquivo do dia.
    """
    return pasta / f"{dia.isoformat()}_{modelo}_{versao}.json"


def salvar(arquivo: Path, resultado: dict[str, Any]) -> None:
    """grava o resultado com as metricas recalculadas.

    Args:
        arquivo: arquivo de resultado.
        resultado: conteudo a gravar.
    """
    resultado["metricas"] = metricas(resultado["fichas"])
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    texto = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"
    arquivo.write_text(texto, encoding="utf-8")


def rodar(  # noqa: PLR0913
    fichas: list[FichaEval],
    paciente_de: Callable[[FichaEval], Paciente],
    *,
    execucoes: int,
    arquivo: Path,
    ritmos: tuple[Ritmo, Ritmo],
    esperas_cota: tuple[float, ...] = ESPERAS_COTA_S,
    db: BancoMemoria | None = None,
) -> dict[str, Any]:
    """roda um lote e salva depois de cada execucao.

    Se o arquivo do dia ja existe, continua nele e pula o que ja rodou: um lote
    interrompido pela cota retoma de onde parou.

    Args:
        fichas: fichas do lote.
        paciente_de: monta o paciente de cada ficha.
        execucoes: execucoes por caso.
        arquivo: arquivo de resultado.
        ritmos: ritmo do paciente e do juiz.
        esperas_cota: esperas entre tentativas em erro de cota.
        db: onde o cliente do llm registra os tokens (o mesmo do paciente).

    Returns:
        resultado completo.
    """
    db = BancoMemoria() if db is None else db
    if arquivo.exists():
        resultado = json.loads(arquivo.read_text(encoding="utf-8"))
    else:
        resultado = {"fichas": [], "ataques": []}
    feitas = {(f["id"], f["execucao"]) for f in resultado["fichas"]}
    for ficha in fichas:
        paciente = paciente_de(ficha)
        resultado.update(
            data=arquivo.name[:10],  # a data do nome, para o lote retomado
            modelo_paciente=paciente.modelo,
            modelo_juiz=juiz.modelo_do_juiz(),
            versao_prompt=paciente.versao_prompt,
            versao_prompt_juiz=juiz.VERSAO_PROMPT,
            execucoes_por_caso=execucoes,
        )
        for execucao in range(1, execucoes + 1):
            if (ficha.id, execucao) in feitas:
                logger.info("{} execucao {} ja feita, pulando", ficha.id, execucao)
                continue
            logger.info("{} execucao {}", ficha.id, execucao)
            linha = rodar_ficha(
                ficha,
                paciente,
                execucao,
                db=db,
                ritmos=ritmos,
                esperas_cota=esperas_cota,
            )
            resultado["fichas"].append(linha)
            resultado["uso_do_lote"] = uso(db)
            salvar(arquivo, resultado)
    return resultado


def ler_fichas(ids: list[str] | None, pasta: Path) -> list[FichaEval]:
    """le as fichas pedidas, ou todas.

    Args:
        ids: ids das fichas; vazio le todas.
        pasta: pasta das fichas.

    Returns:
        fichas validadas no schema.
    """
    arquivos = (
        [pasta / f"{i}.json" for i in ids] if ids else sorted(pasta.glob("*.json"))
    )
    return [
        FichaEval.model_validate_json(a.read_text(encoding="utf-8")) for a in arquivos
    ]


def main(argv: list[str] | None = None) -> int:
    """linha de comando do runner.

    Args:
        argv: argumentos; vazio usa os do terminal.

    Returns:
        codigo de saida (1 quando a cota acabou no meio).
    """
    p = argparse.ArgumentParser(description="roda as fichas de eval")
    p.add_argument("--fichas", nargs="*", help="ids das fichas (padrao: todas)")
    p.add_argument("--execucoes", type=int, default=3, help="execucoes por caso")
    p.add_argument(
        "--paciente",
        choices=["falso", "real"],
        default="falso",
        help="falso: respostas fixas, sem llm; real: paciente da NS-020 no gemini",
    )
    p.add_argument(
        "--pausa-paciente",
        type=float,
        default=PAUSA_PACIENTE_S,
        help="segundos entre chamadas ao paciente (padrao: 15, 4 por minuto)",
    )
    p.add_argument(
        "--pausa-juiz",
        type=float,
        default=PAUSA_JUIZ_S,
        help="segundos entre chamadas ao juiz (padrao: 5, 12 por minuto)",
    )
    p.add_argument("--saida", type=Path, default=PASTA_EVALS / "resultados")
    args = p.parse_args(argv)

    fichas = ler_fichas(args.fichas, PASTA_EVALS / "fichas")
    juiz.modelo_do_juiz()  # falha antes de gastar cota se o ambiente estiver errado
    db = BancoMemoria()
    if args.paciente == "real":
        paciente_de: Callable[[FichaEval], Paciente] = partial(PacienteReal, db=db)
        modelo, versao = os.environ["LLM_MODELO"], PacienteReal.versao_prompt
        pausa_paciente = args.pausa_paciente
    else:
        paciente_de = PacienteFalso
        modelo, versao = PacienteFalso.modelo, PacienteFalso.versao_prompt
        pausa_paciente = 0  # o falso nao chama o llm
    ritmos = (Ritmo(pausa_paciente), Ritmo(args.pausa_juiz))
    arquivo = caminho_resultado(args.saida, date.today(), modelo, versao)
    try:
        rodar(
            fichas,
            paciente_de,
            execucoes=args.execucoes,
            arquivo=arquivo,
            ritmos=ritmos,
            db=db,
        )
    except CotaEsgotadaError:
        logger.error("cota esgotada; rode de novo depois, o que foi feito e pulado")
        return 1
    logger.info("resultado em {}", arquivo)
    return 0
