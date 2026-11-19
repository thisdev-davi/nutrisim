"""guarda o plano e os cenarios na sessao

Revision ID: f1c4a7d2e9b3
Revises: e3b8f1a2c4d5
Create Date: 2026-11-09 12:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "f1c4a7d2e9b3"
down_revision: str | Sequence[str] | None = "e3b8f1a2c4d5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """colunas opcionais: sessoes antigas ficam sem plano."""
    op.add_column("sessoes", sa.Column("plano", postgresql.JSONB(), nullable=True))
    op.add_column("sessoes", sa.Column("cenarios", postgresql.JSONB(), nullable=True))


def downgrade() -> None:
    """remove as colunas."""
    op.drop_column("sessoes", "cenarios")
    op.drop_column("sessoes", "plano")
