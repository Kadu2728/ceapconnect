"""Regra de negócio relacionada ao perfil do usuário autenticado (EPIC 02).

Hoje é uma simples conversão de entidade para schema de resposta, mas fica
isolada em service (em vez de inline no router) para já preparar o terreno
para regras futuras (ex.: enriquecer o perfil com dados de outras EPICs).
"""

from app.models.user import User
from app.schemas.user import UserMe


def get_current_user_profile(user: User) -> UserMe:
    """Converte o usuário autenticado no schema de resposta de `GET /users/me`."""
    return UserMe.model_validate(user)
