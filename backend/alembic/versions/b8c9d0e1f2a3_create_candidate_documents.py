"""create candidate_documents

Revision ID: b8c9d0e1f2a3
Revises: a7b8c9d0e1f2
Create Date: 2026-08-09 00:00:00.000000

Migration escrita manualmente (mesmo padrão das anteriores). EPIC 15 (Upload
de documentos). Espelha `app.models.candidate_document.CandidateDocument`.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "b8c9d0e1f2a3"
down_revision: str | None = "a7b8c9d0e1f2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "candidate_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "candidate_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("document_type", sa.String(length=40), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("file_data", sa.LargeBinary(), nullable=False),
        sa.Column(
            "uploaded_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "document_type IN ('documento_identidade', 'comprovante_residencia', 'foto_3x4')",
            name="ck_candidate_document_type",
        ),
        sa.UniqueConstraint(
            "candidate_profile_id", "document_type", name="uq_candidate_document_profile_type"
        ),
    )
    op.create_index(
        op.f("ix_candidate_documents_candidate_profile_id"),
        "candidate_documents",
        ["candidate_profile_id"],
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_candidate_documents_candidate_profile_id"), table_name="candidate_documents"
    )
    op.drop_table("candidate_documents")
