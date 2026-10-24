"""cria tabelas de alimentos."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "1a7c3e9b5d2f"
down_revision: str | Sequence[str] | None = "dd4596ebf3c4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "categorias",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "alimentos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categorias.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "nutrientes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("umidade", sa.Float(), nullable=True),
        sa.Column("kcal", sa.Float(), nullable=True),
        sa.Column("kj", sa.Float(), nullable=True),
        sa.Column("proteina", sa.Float(), nullable=True),
        sa.Column("lipidios", sa.Float(), nullable=True),
        sa.Column("colesterol", sa.Float(), nullable=True),
        sa.Column("carboidratos", sa.Float(), nullable=True),
        sa.Column("fibra_alimentar", sa.Float(), nullable=True),
        sa.Column("cinzas", sa.Float(), nullable=True),
        sa.Column("calcio", sa.Float(), nullable=True),
        sa.Column("magnesio", sa.Float(), nullable=True),
        sa.Column("manganes", sa.Float(), nullable=True),
        sa.Column("fosforo", sa.Float(), nullable=True),
        sa.Column("ferro", sa.Float(), nullable=True),
        sa.Column("sodio", sa.Float(), nullable=True),
        sa.Column("potassio", sa.Float(), nullable=True),
        sa.Column("cobre", sa.Float(), nullable=True),
        sa.Column("zinco", sa.Float(), nullable=True),
        sa.Column("retinol", sa.Float(), nullable=True),
        sa.Column("re", sa.Float(), nullable=True),
        sa.Column("rae", sa.Float(), nullable=True),
        sa.Column("tiamina", sa.Float(), nullable=True),
        sa.Column("riboflavina", sa.Float(), nullable=True),
        sa.Column("piridoxina", sa.Float(), nullable=True),
        sa.Column("niacina", sa.Float(), nullable=True),
        sa.Column("vitamina_c", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["id"], ["alimentos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("nutrientes")
    op.drop_table("alimentos")
    op.drop_table("categorias")
