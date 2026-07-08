"""Agregador dos models SQLAlchemy do projeto.

Importar cada novo model aqui garante que ele fique registrado em
`Base.metadata`, necessário para o Alembic localizar as tabelas (tanto no
autogenerate quanto para conferência manual das migrations).
"""

from app.models.achievement import Achievement
from app.models.candidate_achievement import CandidateAchievement
from app.models.candidate_profile import CandidateProfile
from app.models.event import Event
from app.models.event_registration import EventRegistration
from app.models.journey_step import JourneyStep
from app.models.mission import Mission
from app.models.mission_progress import MissionProgress
from app.models.notification import Notification
from app.models.user import User

__all__ = [
    "Achievement",
    "CandidateAchievement",
    "CandidateProfile",
    "Event",
    "EventRegistration",
    "JourneyStep",
    "Mission",
    "MissionProgress",
    "Notification",
    "User",
]
