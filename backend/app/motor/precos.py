"""preco aproximado por 100 g dos alimentos da TACO (data/precos.csv).

fontes, uma por linha do csv:
- DIEESE, cesta basica de vitoria-es, preco medio de set/2026;
- procon-sp/DIEESE, cesta basica de sao paulo, set/2026, para o que o DIEESE
  nao cobre em vitoria;
- CEASA-ES (via agrolink), atacado de 30/10/2026, para frutas e hortalicas;
  atacado sai mais barato que o varejo.

conversao para 100 g (a coluna fonte guarda o preco original e a unidade):
- kg: preco / 10;
- pacote, pote ou lata em gramas: preco / gramas * 100;
- leite, 1 litro = 1030 g (densidade 1,03 g/ml);
- oleo de soja, lata de 900 ml = 828 g (densidade 0,92 g/ml);
- ovo, duzia = 660 g (ovo tipo grande, 55 g, piso da classe no mapa).

o preco vale para o alimento cru, como e comprado. carne de primeira (DIEESE)
vale para coxao mole e patinho; carne de segunda (procon-sp) para acem e musculo.
alimento sem fonte fica fora da tabela: quem soma o custo avisa que esta incompleto.
"""

import csv
import math
from collections.abc import Mapping
from functools import cache
from pathlib import Path
from types import MappingProxyType

CSV_PRECOS = Path(__file__).resolve().parents[2] / "data" / "precos.csv"


def ler_precos(caminho: Path) -> dict[int, float]:
    """le o csv de precos.

    Args:
        caminho: csv com alimento_id e preco_100g_reais.

    Returns:
        alimento_id -> R$ por 100 g.

    Raises:
        ValueError: se um preco nao for positivo e finito ou se um id repetir.
    """
    tabela: dict[int, float] = {}
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        for linha in csv.DictReader(arquivo):
            alimento_id = int(linha["alimento_id"])
            preco = float(linha["preco_100g_reais"])
            if not (math.isfinite(preco) and preco > 0):
                raise ValueError(f"alimento {alimento_id}: preço {preco} inválido")
            if alimento_id in tabela:
                raise ValueError(f"alimento {alimento_id} repetido")
            tabela[alimento_id] = preco
    return tabela


@cache
def precos() -> Mapping[int, float]:
    """tabela de data/precos.csv, lida uma vez so.

    Returns:
        alimento_id -> R$ por 100 g, somente leitura (o cache e do processo todo).
    """
    return MappingProxyType(ler_precos(CSV_PRECOS))
