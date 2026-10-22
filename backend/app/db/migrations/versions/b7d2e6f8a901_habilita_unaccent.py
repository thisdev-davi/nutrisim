"""habilita a normalizacao de nomes sem acentos."""

from collections.abc import Sequence

from alembic import op

revision: str = "b7d2e6f8a901"
down_revision: str | Sequence[str] | None = "9f4a2b7c1d8e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """habilita a extensao usada nas buscas de alimentos."""
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent")


def downgrade() -> None:
    """remove a extensao usada nas buscas de alimentos."""
    op.execute("DROP EXTENSION IF EXISTS unaccent")
