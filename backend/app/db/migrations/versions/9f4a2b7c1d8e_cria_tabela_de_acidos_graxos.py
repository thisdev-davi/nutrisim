"""cria tabela de acidos graxos.

Revision ID: 9f4a2b7c1d8e
Revises: dd4596ebf3c4
Create Date: 2026-10-16 20:10:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "9f4a2b7c1d8e"
down_revision: str | Sequence[str] | None = "dd4596ebf3c4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "acidos_graxos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("gordura_saturada", sa.Float(), nullable=True),
        sa.Column("gordura_monoinsaturada", sa.Float(), nullable=True),
        sa.Column("gordura_poliinsaturada", sa.Float(), nullable=True),
        sa.Column("acido_laurico", sa.Float(), nullable=True),
        sa.Column("acido_miristico", sa.Float(), nullable=True),
        sa.Column("acido_palmitico", sa.Float(), nullable=True),
        sa.Column("acido_estearico", sa.Float(), nullable=True),
        sa.Column("acido_araquidico", sa.Float(), nullable=True),
        sa.Column("acido_behenico", sa.Float(), nullable=True),
        sa.Column("acido_lignocerico", sa.Float(), nullable=True),
        sa.Column("acido_miristoleico", sa.Float(), nullable=True),
        sa.Column("acido_palmitoleico", sa.Float(), nullable=True),
        sa.Column("acido_oleico", sa.Float(), nullable=True),
        sa.Column("acido_eicosenoico", sa.Float(), nullable=True),
        sa.Column("acido_linoleico", sa.Float(), nullable=True),
        sa.Column("acido_linolenico", sa.Float(), nullable=True),
        sa.Column("acido_araquidonico", sa.Float(), nullable=True),
        sa.Column("acido_epa", sa.Float(), nullable=True),
        sa.Column("acido_dpa", sa.Float(), nullable=True),
        sa.Column("acido_dha", sa.Float(), nullable=True),
        sa.Column("acido_oleico_trans", sa.Float(), nullable=True),
        sa.Column("acido_linoleico_trans", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["id"], ["alimentos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("acidos_graxos")
