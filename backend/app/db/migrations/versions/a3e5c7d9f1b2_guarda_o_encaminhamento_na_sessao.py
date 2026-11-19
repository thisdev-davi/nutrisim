"""guarda o encaminhamento na sessao (NS-071)

Revision ID: a3e5c7d9f1b2
Revises: f1c4a7d2e9b3
Create Date: 2026-11-19 12:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a3e5c7d9f1b2"
down_revision: str | Sequence[str] | None = "f1c4a7d2e9b3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """coluna opcional: so as sessoes encaminhadas preenchem."""
    op.add_column("sessoes", sa.Column("encaminhamento", sa.Text(), nullable=True))


def downgrade() -> None:
    """remove a coluna."""
    op.drop_column("sessoes", "encaminhamento")
