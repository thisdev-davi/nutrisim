"""Importa categorias e alimentos da base TACO para o banco."""

import csv
from pathlib import Path

from loguru import logger
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.db.deps import obter_engine
from app.db.modelos import AcidosGraxos, Alimentos, Categorias, Nutrientes

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "taco"


def ler_csv(nome: str) -> list[dict[str, str]]:
    """Lê um CSV da base TACO.

    Returns:
        Linhas do arquivo representadas como dicionários.
    """
    with (DATA_DIR / nome).open(encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


def importar_categorias(sessao: Session) -> None:
    """Insere ou atualiza as categorias da base TACO."""
    registros = [
        {"id": int(linha["id"]), "nome": linha["name"]}
        for linha in ler_csv("categories.csv")
    ]
    if not registros:
        return

    comando = insert(Categorias).values(registros)
    comando = comando.on_conflict_do_update(
        index_elements=[Categorias.id],
        set_={"nome": comando.excluded.nome},
    )
    sessao.execute(comando)
    logger.info("Categorias importadas: {}", len(registros))


def importar_alimentos(sessao: Session) -> None:
    """Insere ou atualiza os alimentos da base TACO."""
    registros = [
        {
            "id": int(linha["id"]),
            "category_id": int(linha["categoryId"]),
            "nome": linha["name"],
        }
        for linha in ler_csv("food.csv")
    ]
    if not registros:
        return

    comando = insert(Alimentos).values(registros)
    comando = comando.on_conflict_do_update(
        index_elements=[Alimentos.id],
        set_={
            "category_id": comando.excluded.category_id,
            "nome": comando.excluded.nome,
        },
    )
    sessao.execute(comando)
    logger.info("Alimentos importados: {}", len(registros))


def converter_float(valor: str) -> float | None:
    """Converte um valor da TACO, tratando campos vazios, ``Tr`` e ``NA``.

    Returns:
        Valor convertido, zero para traço ou ``None`` para dado ausente.
    """
    valor = valor.strip().lower()
    if valor == "tr":
        return 0.0
    return float(valor) if valor and valor != "na" else None


def importar_nutrientes(sessao: Session) -> None:
    """Insere ou atualiza os nutrientes da base TACO."""
    campos = {
        "moisture": "umidade",
        "kcal": "kcal",
        "kJ": "kj",
        "protein": "proteina",
        "lipids": "lipidios",
        "cholesterol": "colesterol",
        "carbohydrates": "carboidratos",
        "dietaryFiber": "fibra_alimentar",
        "ash": "cinzas",
        "calcium": "calcio",
        "magnesium": "magnesio",
        "manganese": "manganes",
        "phosphorus": "fosforo",
        "iron": "ferro",
        "sodium": "sodio",
        "potassium": "potassio",
        "copper": "cobre",
        "zinc": "zinco",
        "retinol": "retinol",
        "re": "re",
        "rae": "rae",
        "thiamin": "tiamina",
        "riboflavin": "riboflavina",
        "pyridoxine": "piridoxina",
        "niacin": "niacina",
        "vitaminC": "vitamina_c",
    }
    registros = []
    for linha in ler_csv("nutrients.csv"):
        registro = {"id": int(linha["foodId"])}
        registro.update({
            campo_destino: converter_float(linha[campo_origem])
            for campo_origem, campo_destino in campos.items()
        })
        registros.append(registro)

    if not registros:
        return

    comando = insert(Nutrientes).values(registros)
    comando = comando.on_conflict_do_update(
        index_elements=[Nutrientes.id],
        set_={campo: getattr(comando.excluded, campo) for campo in campos.values()},
    )
    sessao.execute(comando)
    logger.info("Registros de nutrientes importados: {}", len(registros))


def importar_acidos_graxos(sessao: Session) -> None:
    """Insere ou atualiza os ácidos graxos da base TACO."""
    campos = {
        "saturated": "gordura_saturada",
        "monounsaturated": "gordura_monoinsaturada",
        "polyunsaturated": "gordura_poliinsaturada",
        "12:0": "acido_laurico",
        "14:0": "acido_miristico",
        "16:0": "acido_palmitico",
        "18:0": "acido_estearico",
        "20:0": "acido_araquidico",
        "22:0": "acido_behenico",
        "24:0": "acido_lignocerico",
        "14:1": "acido_miristoleico",
        "16:1": "acido_palmitoleico",
        "18:1": "acido_oleico",
        "20:1": "acido_eicosenoico",
        "18:2n6": "acido_linoleico",
        "18:3n3": "acido_linolenico",
        "20:4": "acido_araquidonico",
        "20:5": "acido_epa",
        "22:5": "acido_dpa",
        "22:6": "acido_dha",
        "18:1t": "acido_oleico_trans",
        "18:2t": "acido_linoleico_trans",
    }
    registros = []
    for linha in ler_csv("fatty-acids.csv"):
        registro = {"id": int(linha["foodId"])}
        registro.update({
            campo_destino: converter_float(linha[campo_origem])
            for campo_origem, campo_destino in campos.items()
        })
        registros.append(registro)

    if not registros:
        return

    comando = insert(AcidosGraxos).values(registros)
    comando = comando.on_conflict_do_update(
        index_elements=[AcidosGraxos.id],
        set_={campo: getattr(comando.excluded, campo) for campo in campos.values()},
    )
    sessao.execute(comando)
    logger.info("Registros de ácidos graxos importados: {}", len(registros))


def main() -> None:
    """Importa as tabelas da TACO em uma única transação."""
    with Session(obter_engine()) as sessao:
        try:
            importar_categorias(sessao)
            importar_alimentos(sessao)
            importar_nutrientes(sessao)
            importar_acidos_graxos(sessao)
            sessao.commit()
        except Exception:
            sessao.rollback()
            logger.exception("Falha ao importar dados da TACO")
            raise


if __name__ == "__main__":
    main()
