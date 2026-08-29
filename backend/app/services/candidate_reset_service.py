"""Reset operacional de uma conta de candidato de teste para o estado de
recém-cadastrado — usado antes de demonstrações, nunca em produção real.

Apaga o `CandidateProfile` (hard delete, não soft-delete) e recria via
`bootstrap_new_candidate`, a mesma função usada no cadastro real — em vez de
zerar campo por campo em N tabelas na mão, o que exigiria lembrar de
atualizar este service toda vez que uma tabela nova referenciar
`candidate_profile_id`. Isso funciona porque **toda** FK que aponta para
`candidate_profiles.id` já é `ondelete="CASCADE"` (missões, conquistas,
recompensas, documentos, eventos de atividade, notificações, lembretes,
simulados, contato do responsável + vínculo, score de risco...) — apagar o
profile arrasta tudo junto, de forma atômica e garantida pelo próprio banco.

O `User` (login/e-mail/senha/CPF) nunca é tocado — só o progresso.
"""

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.models.user import ROLE_CANDIDATE, ROLE_GUARDIAN, User
from app.repositories.candidate_profile_repository import CandidateProfileRepository
from app.repositories.user_repository import UserRepository
from app.schemas.candidate_reset import CandidateResetSummary
from app.services.candidate_profile_service import bootstrap_new_candidate


async def reset_candidate_to_zero(
    db: AsyncSession, email: str, *, also_remove_guardian_emails: list[str] | None = None
) -> CandidateResetSummary:
    """Reseta a conta de candidato `email` para o estado de recém-cadastrado.

    Levanta `NotFoundException` se o e-mail não existir, e `BadRequestException`
    se não for uma conta de candidato — proteção contra apontar sem querer
    para uma conta de outro papel.
    """
    user = await UserRepository(db).get_by_email(email)
    if user is None:
        raise NotFoundException(f"Nenhuma conta encontrada com o e-mail {email!r}.")
    if user.role != ROLE_CANDIDATE:
        raise BadRequestException(
            f"{email!r} não é uma conta de candidato (role={user.role!r}) — reset recusado."
        )

    existing_profile = await CandidateProfileRepository(db).get_by_user_id(user.id)
    if existing_profile is not None:
        await db.delete(existing_profile)
        await db.flush()

    removed_guardians = 0
    if also_remove_guardian_emails:
        result = await db.execute(
            delete(User).where(
                User.role == ROLE_GUARDIAN, User.email.in_(also_remove_guardian_emails)
            )
        )
        removed_guardians = result.rowcount or 0

    fresh_profile = await bootstrap_new_candidate(db, user.id)
    await db.commit()
    await db.refresh(fresh_profile)

    return CandidateResetSummary(
        email=email,
        candidate_profile_id=str(fresh_profile.id),
        exam_date=fresh_profile.exam_date,
        interview_date=fresh_profile.interview_date,
        guardian_test_accounts_removed=removed_guardians,
    )
