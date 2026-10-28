"""cria a tabela de usuarios e liga as sessoes a eles.

As sessoes de antes da NS-035 nao tem dono e ninguem mais as acessaria: sao
apagadas com as mensagens. O registro de tokens fica, so perde a sessao.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e3b8f1a2c4d5"
down_revision: str | Sequence[str] | None = "9d729992b10d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """cria usuarios e a coluna usuario_id em sessoes."""
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nome", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("senha_hash", sa.String(), nullable=False),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    # entra vazia, as orfas saem, e so entao vira obrigatoria
    op.add_column("sessoes", sa.Column("usuario_id", sa.Uuid(), nullable=True))
    orfas = "SELECT id FROM sessoes WHERE usuario_id IS NULL"
    op.execute(f"UPDATE chamadas_llm SET sessao_id = NULL WHERE sessao_id IN ({orfas})")  # noqa: S608, E501
    op.execute(f"DELETE FROM mensagens WHERE sessao_id IN ({orfas})")  # noqa: S608
    op.execute("DELETE FROM sessoes WHERE usuario_id IS NULL")
    op.alter_column("sessoes", "usuario_id", nullable=False)
    op.create_index(
        op.f("ix_sessoes_usuario_id"), "sessoes", ["usuario_id"], unique=False
    )
    op.create_foreign_key(
        "sessoes_usuario_id_fkey", "sessoes", "usuarios", ["usuario_id"], ["id"]
    )


def downgrade() -> None:
    """remove a ligacao das sessoes e a tabela de usuarios."""
    op.drop_constraint("sessoes_usuario_id_fkey", "sessoes", type_="foreignkey")
    op.drop_index(op.f("ix_sessoes_usuario_id"), table_name="sessoes")
    op.drop_column("sessoes", "usuario_id")
    op.drop_table("usuarios")
