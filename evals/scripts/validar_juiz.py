# valida o juiz do eval (NS-033); a logica fica em backend/app/eval/validacao_juiz.py
# uso, de dentro de backend: uv run python ../evals/scripts/validar_juiz.py --help
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

from app.eval.validacao_juiz import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
