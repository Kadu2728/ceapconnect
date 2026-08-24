"""extend activity_events vocabulary (Candidate Journey OS — fase F1)

Revision ID: a8b9c0d1e2f3
Revises: d6e7f8a9b0c1
Create Date: 2026-08-24 00:00:00.000000

Migração puramente aditiva: só troca a `CHECK CONSTRAINT` de
`activity_events.name` para aceitar os novos nomes consumidos pelo
Candidate State (N1), Next Best Action Engine (N2), Zero-Click Recovery
(N3) e Modo Resgate (N4) — ver `app.models.activity_event`. Nenhuma linha
existente é tocada, nenhum nome antigo é removido ou renomeado.
"""

from collections.abc import Sequence

from alembic import op

revision: str = "a8b9c0d1e2f3"
down_revision: str | None = "d6e7f8a9b0c1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_OLD_NAMES = (
    "login",
    "step_viewed",
    "step_completed",
    "mission_started",
    "mission_completed",
    "mission_abandoned",
    "document_uploaded",
)

_NEW_NAMES = (
    "step_abandoned",
    "step_resumed",
    "nba_generated",
    "nba_clicked",
    "nba_completed",
    "recovery_entered",
    "recovery_completed",
    "recovery_exited",
)


def upgrade() -> None:
    op.drop_constraint("ck_activity_event_name", "activity_events", type_="check")
    all_names = _OLD_NAMES + _NEW_NAMES
    op.create_check_constraint(
        "ck_activity_event_name",
        "activity_events",
        "name IN " + str(all_names),
    )


def downgrade() -> None:
    op.drop_constraint("ck_activity_event_name", "activity_events", type_="check")
    op.create_check_constraint(
        "ck_activity_event_name",
        "activity_events",
        "name IN " + str(_OLD_NAMES),
    )
