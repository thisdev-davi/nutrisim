# roda o eval (NS-026); a logica fica em backend/app/eval/runner.py
# uso, de dentro de backend/: uv run python ../evals/scripts/rodar_eval.py --help
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

from app.eval.runner import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
