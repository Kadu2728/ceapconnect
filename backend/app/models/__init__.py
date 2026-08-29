"""Agregador dos models SQLAlchemy do projeto.

Importar cada novo model aqui garante que ele fique registrado em
`Base.metadata`, necessário para o Alembic localizar as tabelas (tanto no
autogenerate quanto para conferência manual das migrations).
"""

from app.models.achievement import Achievement
from app.models.activity_event import ActivityEvent
from app.models.candidate_achievement import CandidateAchievement
from app.models.candidate_document import CandidateDocument
from app.models.candidate_profile import CandidateProfile
from app.models.chat_message import ChatMessage
from app.models.cohort import Cohort, CoordinatorCohort
from app.models.cohort_xp_standing import CohortXpStanding
from app.models.event import Event
from app.models.event_registration import EventRegistration
from app.models.guardian import Guardian
from app.models.guardian_candidate_link import GuardianCandidateLink
from app.models.guardian_intervention import GuardianIntervention
from app.models.intervention import Intervention
from app.models.journey_step import JourneyStep
from app.models.mission import Mission
from app.models.mission_progress import MissionProgress
from app.models.notification import Notification
from app.models.push_subscription import PushSubscription
from app.models.reminder_log import ReminderLog
from app.models.reward import Reward
from app.models.reward_redemption import RewardRedemption
from app.models.risk_score import RiskScore
from app.models.risk_score_history import RiskScoreHistory
from app.models.simulado import SimuladoAnswer, SimuladoAttempt, SimuladoQuestion
from app.models.user import User

__all__ = [
    "Achievement",
    "ActivityEvent",
    "CandidateAchievement",
    "CandidateDocument",
    "CandidateProfile",
    "ChatMessage",
    "Cohort",
    "CohortXpStanding",
    "CoordinatorCohort",
    "Event",
    "EventRegistration",
    "Guardian",
    "GuardianCandidateLink",
    "GuardianIntervention",
    "Intervention",
    "JourneyStep",
    "Mission",
    "MissionProgress",
    "Notification",
    "PushSubscription",
    "ReminderLog",
    "Reward",
    "RewardRedemption",
    "RiskScore",
    "RiskScoreHistory",
    "SimuladoAnswer",
    "SimuladoAttempt",
    "SimuladoQuestion",
    "User",
]
