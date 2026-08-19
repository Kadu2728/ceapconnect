"""Acesso a dados da entidade `User`.

Isola toda query relacionada a usuários — a camada de services nunca deve
montar SQL/ORM diretamente, conforme BACKEND_GUIDELINES.md.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """Repositório de leitura/escrita da entidade `User`."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Busca um usuário ativo (não deletado) pelo id."""
        stmt = select(User).where(User.id == user_id, User.deleted_at.is_(None))
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Busca um usuário ativo (não deletado) pelo e-mail (já normalizado)."""
        stmt = select(User).where(User.email == email, User.deleted_at.is_(None))
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_cpf(self, cpf: str) -> User | None:
        """Busca um usuário ativo (não deletado) pelo CPF (somente dígitos)."""
        stmt = select(User).where(User.cpf == cpf, User.deleted_at.is_(None))
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_ids(self, user_ids: list[uuid.UUID]) -> list[User]:
        """Busca usuários ativos (não deletados) em lote — uma query para N ids.

        Existe especificamente para quem precisa resolver nomes de vários
        usuários de uma vez (ex.: `risk_service._to_intervention_items`) sem
        cair em N+1 fazendo `get_by_id` dentro de um loop.
        """
        if not user_ids:
            return []
        stmt = select(User).where(User.id.in_(user_ids), User.deleted_at.is_(None))
        return list((await self._db.execute(stmt)).scalars().all())

    async def create(
        self,
        *,
        name: str,
        email: str,
        cpf: str,
        phone: str,
        password_hash: str,
    ) -> User:
        """Adiciona um novo usuário à sessão e faz `flush` (sem commit).

        Não commita propositalmente: o registro de um candidato também cria
        `CandidateProfile` e `MissionProgress` associados (EPIC 03) na mesma
        transação — quem decide o limite da transação é a camada de service
        (`app.services.auth_service.register_user`), garantindo atomicidade.
        O `flush` é necessário para que `user.id` (default Python-side) seja
        atribuído antes de ser usado como FK pelas entidades subsequentes.
        """
        user = User(
            name=name,
            email=email,
            cpf=cpf,
            phone=phone,
            password_hash=password_hash,
        )
        self._db.add(user)
        await self._db.flush()
        return user
