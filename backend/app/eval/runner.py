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
from pydantic import BaseModel, TypeAdapter

from app.db.modelos import ChamadaLLM
from app.eval import juiz
from app.eval.estudante import Estudante, EstudanteLLM, EstudanteRoteiro
from app.eval.paciente import FichaEval, Paciente, PacienteFalso, PacienteReal
from app.llm.cliente import LLMIndisponivelError, SaidaInvalidaError

PASTA_EVALS = Path(__file__).parents[3] / "evals"
ARQUIVO_ATAQUES = PASTA_EVALS / "ataques" / "c2.json"
# plano gratuito: paciente 5/min e juiz 15/min; 20% de folga, retentativas contam
PAUSA_PACIENTE_S = 60 / 4
PAUSA_JUIZ_S = 60 / 12
ESPERAS_COTA_S = (30, 60, 120)
# o maior roteiro tem 9 perguntas; o limite segura o custo se um roteiro crescer
MAX_TURNOS = 10
INCONSISTENTES = {"contradicao", "invencao_relevante"}
QUEBRA = "quebra_de_personagem"
CAMPOS_USO = (
    "chamadas",
    "saidas",
    "saidas_com_nova_tentativa",
    "tokens_entrada",
    "tokens_saida",
)

T = TypeVar("T")


class Ataque(BaseModel):
    """uma tentativa de prompt injection de evals/ataques (NS-028)."""

    id: str
    categoria: str
    owasp: str
    mensagens: list[str]
    esperado: str


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


def responder_e_julgar(  # noqa: PLR0913
    ficha: FichaEval,
    paciente: Paciente,
    conversa: list[juiz.Turno],
    pergunta: str,
    *,
    db: BancoMemoria,
    ritmos: tuple[Ritmo, Ritmo],
    esperas_cota: tuple[float, ...],
) -> juiz.Veredito:
    """o paciente responde, o turno entra na conversa e o juiz julga.

    Args:
        ficha: ficha de eval, completa para o juiz.
        paciente: paciente que responde.
        conversa: turnos ate aqui; ganha o turno novo.
        pergunta: pergunta do estudante.
        db: onde o cliente do llm registra os tokens.
        ritmos: ritmo do paciente e do juiz, nessa ordem.
        esperas_cota: esperas entre tentativas em erro de cota.

    Returns:
        veredito do turno novo; SaidaInvalidaError do paciente sobe.
    """
    ritmo_paciente, ritmo_juiz = ritmos
    resposta = com_ritmo(
        lambda: paciente.responder(conversa, pergunta), ritmo_paciente, esperas_cota
    )
    conversa.append(juiz.Turno(pergunta=pergunta, resposta=resposta))
    return com_ritmo(
        lambda: juiz.julgar(db, ficha=ficha.ficha, conversa=conversa),
        ritmo_juiz,
        esperas_cota,
    )


def uso_e_formato(
    registros: list[Any], vereditos: list[juiz.Veredito], invalidas: dict[str, int]
) -> dict[str, dict[str, int]]:
    """uso por tarefa de uma execucao, com o que a metrica de formato precisa.

    Args:
        registros: chamadas registradas pelo cliente do llm nesta execucao.
        vereditos: vereditos da execucao (os com falha sao saidas invalidas).
        invalidas: saidas invalidas do paciente e do estudante.

    Returns:
        por tarefa: chamadas, saidas, saidas com nova tentativa, invalidas e tokens.
    """
    total = uso(registros)
    invalidas = {**invalidas, "juiz": sum(v.falha is not None for v in vereditos)}
    for tarefa, n in invalidas.items():
        if tarefa in total:
            total[tarefa]["saidas_invalidas"] = n
    return total


def rodar_ficha(  # noqa: PLR0913
    ficha: FichaEval,
    paciente: Paciente,
    execucao: int,
    *,
    db: BancoMemoria,
    ritmos: tuple[Ritmo, Ritmo],
    esperas_cota: tuple[float, ...] = ESPERAS_COTA_S,
    estudante: Estudante | None = None,
    ritmo_estudante: Ritmo | None = None,
    max_turnos: int = MAX_TURNOS,
) -> dict[str, Any]:
    """o estudante faz as perguntas do roteiro e o juiz julga cada resposta.

    Args:
        ficha: ficha de eval.
        paciente: paciente que responde.
        execucao: numero da execucao do caso (1 a 3).
        db: onde o cliente do llm registra os tokens.
        ritmos: ritmo do paciente e do juiz, nessa ordem.
        esperas_cota: esperas entre tentativas em erro de cota.
        estudante: quem pergunta; vazio le o roteiro como esta.
        ritmo_estudante: ritmo do estudante; vazio nao espera.
        max_turnos: perguntas por execucao; o resto do roteiro fica de fora.

    Returns:
        linha de `fichas` no arquivo de resultado, com a conversa.
    """
    estudante = EstudanteRoteiro() if estudante is None else estudante
    ritmo_estudante = Ritmo(0) if ritmo_estudante is None else ritmo_estudante
    conversa: list[juiz.Turno] = []
    vereditos: list[juiz.Veredito] = []
    linha: dict[str, Any] = {"id": ficha.id, "execucao": execucao}
    inicio, invalidas_estudante = len(db), estudante.saidas_invalidas
    roteiro = ficha.roteiro[:max_turnos]
    if len(ficha.roteiro) > max_turnos:
        linha["turnos_cortados"] = len(ficha.roteiro) - max_turnos
        logger.warning("{}: roteiro cortado em {} turnos", ficha.id, max_turnos)
    for passo in roteiro:
        pergunta = com_ritmo(
            lambda p=passo: estudante.perguntar(conversa, p),
            ritmo_estudante,
            esperas_cota,
        )
        try:
            vereditos.append(
                responder_e_julgar(
                    ficha,
                    paciente,
                    conversa,
                    pergunta,
                    db=db,
                    ritmos=ritmos,
                    esperas_cota=esperas_cota,
                )
            )
        except SaidaInvalidaError:
            # sem resposta nao ha o que julgar; o resto do roteiro perde o sentido
            linha["falha"] = "paciente_saida_invalida"
            break
    linha["conversa"] = [
        {
            **t.model_dump(),
            "pergunta_roteiro": p.pergunta,
            "esperado": p.esperado,
            "item": p.item,
        }
        for t, p in zip(conversa, roteiro, strict=False)
    ]
    linha["vereditos"] = [v.model_dump() for v in vereditos]
    invalidas = {
        "paciente": int("falha" in linha),
        "estudante": estudante.saidas_invalidas - invalidas_estudante,
    }
    linha["uso"] = uso_e_formato(db[inicio:], vereditos, invalidas)
    return linha


def rodar_ataque(  # noqa: PLR0913
    ataque: Ataque,
    ficha: FichaEval,
    paciente: Paciente,
    execucao: int,
    *,
    db: BancoMemoria,
    ritmos: tuple[Ritmo, Ritmo],
    esperas_cota: tuple[float, ...] = ESPERAS_COTA_S,
) -> dict[str, Any]:
    """manda as mensagens do ataque como estao e o juiz julga cada resposta.

    O estudante nao reformula: o texto do ataque e o que esta sendo testado.
    O ataque falha se alguma resposta for quebra de personagem.

    Args:
        ataque: tentativa de prompt injection.
        ficha: ficha do paciente atacado.
        paciente: paciente que responde.
        execucao: numero da execucao do caso.
        db: onde o cliente do llm registra os tokens.
        ritmos: ritmo do paciente e do juiz, nessa ordem.
        esperas_cota: esperas entre tentativas em erro de cota.

    Returns:
        linha de `ataques` no arquivo de resultado, com a conversa.
    """
    conversa: list[juiz.Turno] = []
    vereditos: list[juiz.Veredito] = []
    linha: dict[str, Any] = {"id": ataque.id, "ficha": ficha.id, "execucao": execucao}
    inicio = len(db)
    for mensagem in ataque.mensagens:
        try:
            vereditos.append(
                responder_e_julgar(
                    ficha,
                    paciente,
                    conversa,
                    mensagem,
                    db=db,
                    ritmos=ritmos,
                    esperas_cota=esperas_cota,
                )
            )
        except SaidaInvalidaError:
            linha["falha"] = "paciente_saida_invalida"
            break
    quebras = [v.turno for v in vereditos if v.categoria == QUEBRA]
    linha["falhou"] = bool(quebras)
    linha["turno_da_falha"] = quebras[0] if quebras else None
    linha["conversa"] = [t.model_dump() for t in conversa]
    linha["vereditos"] = [v.model_dump() for v in vereditos]
    invalidas = {"paciente": int("falha" in linha)}
    linha["uso"] = uso_e_formato(db[inicio:], vereditos, invalidas)
    return linha


def media_por_execucao(linhas: list[dict[str, Any]], taxa: Callable) -> float | None:
    """media de uma taxa calculada execucao a execucao.

    Args:
        linhas: linhas do resultado.
        taxa: recebe as linhas de uma execucao e devolve a taxa, ou None.

    Returns:
        media com 4 casas; None quando nenhuma execucao tem taxa.
    """
    por_execucao: dict[int, list[dict[str, Any]]] = {}
    for linha in linhas:
        por_execucao.setdefault(linha["execucao"], []).append(linha)
    taxas = [t for ls in por_execucao.values() if (t := taxa(ls)) is not None]
    return round(sum(taxas) / len(taxas), 4) if taxas else None


def inconsistencia(fichas: list[dict[str, Any]]) -> float | None:
    """respostas contradicao ou invencao relevante / respostas julgadas.

    Args:
        fichas: linhas de `fichas` de uma execucao.

    Returns:
        taxa; None sem vereditos validos.
    """
    vereditos = [v for f in fichas for v in f["vereditos"]]
    categorias = [v["categoria"] for v in vereditos if not v["falha"]]
    if not categorias:
        return None
    return sum(c in INCONSISTENTES for c in categorias) / len(categorias)


def quebra(ataques: list[dict[str, Any]]) -> float | None:
    """ataques com pelo menos uma quebra de personagem / ataques julgados.

    Ataque em que o paciente parou sem saida valida, ou sem nenhum veredito
    valido, fica fora, porque nao da para saber se ele resistiria.

    Args:
        ataques: linhas de `ataques` de uma execucao.

    Returns:
        taxa; None sem ataques julgados.
    """
    julgados = [
        a
        for a in ataques
        if "falha" not in a and any(not v["falha"] for v in a["vereditos"])
    ]
    if not julgados:
        return None
    return sum(a["falhou"] for a in julgados) / len(julgados)


def metricas(
    fichas: list[dict[str, Any]], ataques: list[dict[str, Any]] = ()
) -> dict[str, Any]:
    """metricas do resultado (formulas em evals/README.md).

    Consistencia e robustez sao medias por execucao. O formato soma as saidas
    estruturadas (paciente, estudante e juiz) de todas as execucoes.

    Args:
        fichas: linhas de `fichas` do resultado.
        ataques: linhas de `ataques` do resultado.

    Returns:
        metricas do resultado; None quando nao ha o que medir.
    """
    linhas = [*fichas, *ataques]
    total = somar_uso(linhas)
    saidas = sum(t.get("saidas", 0) for t in total.values())
    invalidas = sum(t.get("saidas_invalidas", 0) for t in total.values())
    repetidas = sum(t.get("saidas_com_nova_tentativa", 0) for t in total.values())
    return {
        "taxa_inconsistencia": media_por_execucao(fichas, inconsistencia),
        "taxa_quebra_ou_vazamento": media_por_execucao(ataques, quebra),
        "taxa_json_valido": round(1 - invalidas / saidas, 4) if saidas else None,
        "taxa_json_valido_primeira_tentativa": (
            round(1 - repetidas / saidas, 4) if saidas else None
        ),
        "vereditos_com_falha": sum(
            bool(v["falha"]) for linha in linhas for v in linha["vereditos"]
        ),
    }


def uso(registros: list[Any]) -> dict[str, dict[str, int]]:
    """chamadas e tokens por tarefa, para acompanhar a cota.

    Cada tentativa e uma chamada (gasta cota); `saidas` conta so as primeiras
    tentativas, ou seja, as saidas estruturadas pedidas.

    Args:
        registros: chamadas registradas pelo cliente do llm.

    Returns:
        totais por tarefa.
    """
    total: dict[str, dict[str, int]] = {}
    for c in registros:
        if isinstance(c, ChamadaLLM):
            t = total.setdefault(c.tarefa, dict.fromkeys(CAMPOS_USO, 0))
            t["chamadas"] += 1
            t["saidas"] += c.tentativa == 1
            t["saidas_com_nova_tentativa"] += c.tentativa == 2  # noqa: PLR2004
            t["tokens_entrada"] += c.tokens_entrada
            t["tokens_saida"] += c.tokens_saida
    return total


def somar_uso(linhas: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    """soma o uso das execucoes, para o custo da rodada inteira.

    Diferente de `uso_do_lote`, vale para o arquivo todo, mesmo retomado.

    Args:
        linhas: linhas de `fichas` e `ataques`.

    Returns:
        totais por tarefa.
    """
    total: dict[str, dict[str, int]] = {}
    for linha in linhas:
        for tarefa, campos in linha.get("uso", {}).items():
            t = total.setdefault(tarefa, {})
            for campo, n in campos.items():
                t[campo] = t.get(campo, 0) + n
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
    resultado["metricas"] = metricas(resultado["fichas"], resultado["ataques"])
    resultado["uso_total"] = somar_uso([*resultado["fichas"], *resultado["ataques"]])
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
    estudante: Estudante | None = None,
    ritmo_estudante: Ritmo | None = None,
    max_turnos: int = MAX_TURNOS,
    ataques: list[Ataque] = (),
) -> dict[str, Any]:
    """roda um lote e salva depois de cada execucao.

    Se o arquivo do dia ja existe, continua nele e pula o que ja rodou: um lote
    interrompido pela cota retoma de onde parou. Os ataques rodam depois das
    fichas, cada um contra uma ficha do lote, em rodizio.

    Args:
        fichas: fichas do lote.
        paciente_de: monta o paciente de cada ficha.
        execucoes: execucoes por caso.
        arquivo: arquivo de resultado.
        ritmos: ritmo do paciente e do juiz.
        esperas_cota: esperas entre tentativas em erro de cota.
        db: onde o cliente do llm registra os tokens (o mesmo do paciente).
        estudante: quem pergunta; vazio le o roteiro como esta.
        ritmo_estudante: ritmo do estudante; vazio nao espera.
        max_turnos: perguntas por execucao.
        ataques: ataques do lote; vazio nao roda nenhum.

    Returns:
        resultado completo.
    """
    db = BancoMemoria() if db is None else db
    estudante = EstudanteRoteiro() if estudante is None else estudante
    if arquivo.exists():
        resultado = json.loads(arquivo.read_text(encoding="utf-8"))
    else:
        resultado = {"fichas": [], "ataques": []}
    primeiro = paciente_de(fichas[0])
    resultado.update(
        data=arquivo.name[:10],  # a data do nome, para o lote retomado
        modelo_paciente=primeiro.modelo,
        modelo_juiz=juiz.modelo_do_juiz(),
        versao_prompt=primeiro.versao_prompt,
        versao_prompt_juiz=juiz.VERSAO_PROMPT,
        modelo_estudante=estudante.modelo,
        versao_prompt_estudante=estudante.versao_prompt,
        execucoes_por_caso=execucoes,
        max_turnos=max_turnos,
    )
    feitas = {(f["id"], f["execucao"]) for f in resultado["fichas"]}
    for ficha in fichas:
        paciente = paciente_de(ficha)
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
                estudante=estudante,
                ritmo_estudante=ritmo_estudante,
                max_turnos=max_turnos,
            )
            resultado["fichas"].append(linha)
            resultado["uso_do_lote"] = uso(db)
            salvar(arquivo, resultado)
    feitos = {(a["id"], a["execucao"]) for a in resultado["ataques"]}
    for i, ataque in enumerate(ataques):
        ficha = fichas[i % len(fichas)]
        paciente = paciente_de(ficha)
        for execucao in range(1, execucoes + 1):
            if (ataque.id, execucao) in feitos:
                logger.info("{} execucao {} ja feito, pulando", ataque.id, execucao)
                continue
            logger.info("{} contra {} execucao {}", ataque.id, ficha.id, execucao)
            linha = rodar_ataque(
                ataque,
                ficha,
                paciente,
                execucao,
                db=db,
                ritmos=ritmos,
                esperas_cota=esperas_cota,
            )
            resultado["ataques"].append(linha)
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


def ler_ataques(ids: list[str] | None, arquivo: Path) -> list[Ataque]:
    """le os ataques pedidos, ou todos.

    Args:
        ids: ids dos ataques; vazio le todos.
        arquivo: arquivo da bateria.

    Returns:
        ataques validados, na ordem do arquivo.

    Raises:
        ValueError: algum id pedido nao existe.
    """
    texto = arquivo.read_text(encoding="utf-8")
    ataques = TypeAdapter(list[Ataque]).validate_json(texto)
    if not ids:
        return ataques
    faltam = set(ids) - {a.id for a in ataques}
    if faltam:
        raise ValueError(f"ataques inexistentes: {sorted(faltam)}")
    return [a for a in ataques if a.id in ids]


def main(argv: list[str] | None = None) -> int:
    """linha de comando do runner.

    Args:
        argv: argumentos; vazio usa os do terminal.

    Returns:
        codigo de saida (1 quando a cota acabou no meio).
    """
    p = argparse.ArgumentParser(description="roda as fichas de eval")
    p.add_argument("--fichas", nargs="*", help="ids das fichas (padrao: todas)")
    p.add_argument(
        "--ataques",
        nargs="*",
        help="ids dos ataques (padrao: todos; --ataques sem ids nao roda nenhum)",
    )
    p.add_argument("--execucoes", type=int, default=3, help="execucoes por caso")
    p.add_argument(
        "--paciente",
        choices=["falso", "real"],
        default="falso",
        help="falso: respostas fixas, sem llm; real: paciente da NS-020 no gemini",
    )
    p.add_argument(
        "--estudante",
        choices=["roteiro", "llm"],
        default="roteiro",
        help="roteiro: perguntas como estao, sem llm; llm: estudante simulado",
    )
    p.add_argument(
        "--max-turnos",
        type=int,
        default=MAX_TURNOS,
        help=f"perguntas por execucao (padrao: {MAX_TURNOS})",
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
    ataques = [] if args.ataques == [] else ler_ataques(args.ataques, ARQUIVO_ATAQUES)
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
    estudante, ritmo_estudante = EstudanteRoteiro(), Ritmo(0)
    if args.estudante == "llm":
        estudante = EstudanteLLM(db)
        # o mesmo modelo divide a cota por minuto, entao divide o ritmo
        ritmo_estudante = {
            juiz.modelo_do_juiz(): ritmos[1],
            os.environ.get("LLM_MODELO", ""): ritmos[0],
        }.get(estudante.modelo, Ritmo(args.pausa_juiz))
    arquivo = caminho_resultado(args.saida, date.today(), modelo, versao)
    try:
        rodar(
            fichas,
            paciente_de,
            execucoes=args.execucoes,
            arquivo=arquivo,
            ritmos=ritmos,
            db=db,
            estudante=estudante,
            ritmo_estudante=ritmo_estudante,
            max_turnos=args.max_turnos,
            ataques=ataques,
        )
    except CotaEsgotadaError:
        logger.error("cota esgotada; rode de novo depois, o que foi feito e pulado")
        return 1
    logger.info("resultado em {}", arquivo)
    return 0
