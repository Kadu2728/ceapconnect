"""Acesso a dados da entidade `RiskScore` (EPIC 14 — Predição de evasão).

Isola as queries do estado de risco — a camada de services nunca monta SQL/ORM
diretamente. A leitura da fila (`list_queue`) já traz `CandidateProfile`,
`User` e `Cohort` via join — é a query que sustenta o Console de Intervenção,
então evita N+1 por natureza.
"""

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.risk_scoring import RiskTier
from app.models.candidate_profile import STATUS_ACTIVE, CandidateProfile
from app.models.cohort import Cohort
from app.models.journey_pause import PAUSE_ACTIVE, JourneyPause
from app.models.risk_score import RiskScore
from app.models.risk_score_history import RiskScoreHistory
from app.models.silence_signal import SilenceSignal
from app.models.user import User


class RiskScoreRepository:
    """Repositório de leitura/escrita do estado atual de risco por candidato."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_profile_id(self, candidate_profile_id: uuid.UUID) -> RiskScore | None:
        """Score atual de um candidato (ou None se nunca calculado)."""
        stmt = select(RiskScore).where(RiskScore.candidate_profile_id == candidate_profile_id)
        return (await self._db.execute(stmt)).scalar_one_or_none()

    async def upsert(
        self,
        *,
        candidate_profile_id: uuid.UUID,
        score: int,
        tier: RiskTier,
        factors: list[dict[str, Any]],
        explanation: str,
        features: dict[str, Any],
        model_version: str,
    ) -> RiskScore:
        """Cria ou atualiza o score do candidato (flush, sem commit).

        `risk_scores` é upsert por natureza — guarda o estado *atual*, não um
        histórico (ver `append_history` para a série temporal).
        """
        existing = await self.get_by_profile_id(candidate_profile_id)
        if existing is None:
            existing = RiskScore(candidate_profile_id=candidate_profile_id)
            self._db.add(existing)

        existing.score = score
        existing.tier = tier
        existing.factors = factors
        existing.explanation = explanation
        existing.features = features
        existing.model_version = model_version
        await self._db.flush()
        return existing

    async def append_history(
        self,
        *,
        candidate_profile_id: uuid.UUID,
        score: int,
        tier: RiskTier,
        factors: list[dict[str, Any]],
        explanation: str,
        features: dict[str, Any],
        model_version: str,
    ) -> RiskScoreHistory:
        """Grava um snapshot imutável do score em `risk_score_history` (flush, sem commit).

        Nunca atualiza uma linha existente — cada recálculo é uma nova linha,
        é essa série temporal que sustenta o harness de backtest.
        """
        entry = RiskScoreHistory(
            candidate_profile_id=candidate_profile_id,
            score=score,
            tier=tier,
            factors=factors,
            explanation=explanation,
            features=features,
            model_version=model_version,
        )
        self._db.add(entry)
        await self._db.flush()
        return entry

    async def list_queue(
        self,
        *,
        cohort_ids: list[uuid.UUID] | None,
        tier: RiskTier | None = None,
        cohort_id_filter: uuid.UUID | None = None,
    ) -> list[
        tuple[
            RiskScore,
            CandidateProfile,
            User,
            Cohort | None,
            JourneyPause | None,
            SilenceSignal | None,
        ]
    ]:
        """Fila de risco, mais arriscado primeiro — já filtrada pelo escopo do RBAC.

        `cohort_ids=None` = irrestrito (admin). Uma lista (mesmo vazia) restringe
        às coortes informadas — lista vazia sempre retorna fila vazia, nunca
        "todos" (mesma semântica de `CohortScope`). Só traz candidatos com
        `status=active`: quem já teve o outcome decidido (aprovado/evadido/
        desistente) some da fila imediatamente, sem esperar o próximo
        recálculo periódico.

        Traz junto a pausa declarada em curso (LEFT JOIN, no máximo uma por
        candidato pelo índice único parcial): é ela que permite ao coordenador
        distinguir "avisou que precisava de uns dias" de "sumiu sem avisar" —
        dois estados com a mesma cara na fila, e que pedem abordagens opostas.
        """
        if cohort_ids is not None and len(cohort_ids) == 0:
            return []

        now = datetime.now(UTC)
        stmt = (
            select(RiskScore, CandidateProfile, User, Cohort, JourneyPause, SilenceSignal)
            .join(CandidateProfile, CandidateProfile.id == RiskScore.candidate_profile_id)
            .join(User, User.id == CandidateProfile.user_id)
            .outerjoin(Cohort, Cohort.id == CandidateProfile.cohort_id)
            .outerjoin(
                JourneyPause,
                and_(
                    JourneyPause.candidate_profile_id == CandidateProfile.id,
                    JourneyPause.status == PAUSE_ACTIVE,
                    JourneyPause.ends_at > now,
                ),
            )
            # Sinal de silêncio em aberto (Radar). No máximo um por candidato
            # pelo índice único parcial, então não multiplica linhas.
            .outerjoin(
                SilenceSignal,
                and_(
                    SilenceSignal.candidate_profile_id == CandidateProfile.id,
                    SilenceSignal.returned_at.is_(None),
                ),
            )
            .where(CandidateProfile.status == STATUS_ACTIVE)
            .order_by(RiskScore.score.desc())
        )
        if cohort_ids is not None:
            stmt = stmt.where(CandidateProfile.cohort_id.in_(cohort_ids))
        if cohort_id_filter is not None:
            stmt = stmt.where(CandidateProfile.cohort_id == cohort_id_filter)
        if tier is not None:
            stmt = stmt.where(RiskScore.tier == tier)

        result = await self._db.execute(stmt)
        return [(row[0], row[1], row[2], row[3], row[4], row[5]) for row in result.all()]
