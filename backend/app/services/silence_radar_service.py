"""Radar de Silêncio ("Jornada que Respira" — metade B).

Age sobre a **ausência** de ação: detecta o instante em que um candidato
cruza de ativo para silencioso, para o coordenador poder abordar antes do
abandono se consolidar.

**O que o Radar NÃO faz, porque já existe**: medir, pontuar e exibir
silêncio. `risk_scoring._WEIGHT_INACTIVITY` (35, o maior peso comportamental
do modelo) já faz isso, e o Console já mostra "Sem atividade há N dia(s)" em
linguagem humana. Duplicar essa derivação criaria exatamente a divergência
que `candidate_state_scoring` alerta — por isso este módulo **não deriva
nada**: recebe as `CandidateRiskFeatures` que o job de risco já calculou e só
decide quando a travessia aconteceu.

**O que o Radar acrescenta**: transformar um *estado que o coordenador
precisa procurar* num *evento que chega até ele*. "Quem entrou em silêncio
esta semana" é uma pergunta que a fila ordenada por score não responde.

**Freio central — pausa declarada nunca gera sinal.** Quem avisou que
precisava de uns dias não está em silêncio: está exatamente onde disse que
estaria. Sinalizá-lo faria o produto punir quem foi honesto, que é o oposto
do que a metade A construiu.

Nesta fase o Radar **não envia nada ao candidato nem ao responsável** — só
alimenta o Console. Mensagem automática sobre um menor depende de tato
(frequência e tom), e o sistema ainda não tem quiet hours nem limite de
frequência; ligar isso agora seria escolher o risco antes da evidência.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.candidate_state_scoring import STALLED_INACTIVITY_DAYS
from app.core.risk_scoring import CandidateRiskFeatures
from app.repositories.journey_pause_repository import JourneyPauseRepository
from app.repositories.silence_signal_repository import SilenceSignalRepository


async def sync_signals(db: AsyncSession, features_list: list[CandidateRiskFeatures]) -> int:
    """Abre sinais para quem acabou de emudecer e fecha os de quem voltou.

    Recebe as features **já derivadas** pelo job de risco — nenhuma query de
    comportamento nova. Não commita: participa da transação de
    `risk_service.recompute_all`, que decide o limite.

    Retorna quantos sinais foram abertos nesta passada.
    """
    if not features_list:
        return 0

    profile_ids = [uuid.UUID(f.candidate_profile_id) for f in features_list]
    signal_repo = SilenceSignalRepository(db)
    open_signals = await signal_repo.map_open_by_profile_ids(profile_ids)
    paused_ids = await JourneyPauseRepository(db).set_paused_profile_ids(profile_ids)

    now = datetime.now(UTC)
    opened = 0

    for features in features_list:
        profile_id = uuid.UUID(features.candidate_profile_id)
        existing = open_signals.get(profile_id)
        is_silent = features.days_since_last_activity >= STALLED_INACTIVITY_DAYS

        # Pausa declarada tem precedência sobre tudo: quem avisou não está em
        # silêncio. Um sinal aberto antes da pausa é fechado — a partir do
        # aviso, a ausência deixou de ser inexplicada.
        if profile_id in paused_ids:
            if existing is not None:
                await signal_repo.close(existing, returned_at=now)
            continue

        if is_silent and existing is None:
            await signal_repo.create(
                candidate_profile_id=profile_id,
                detected_at=now,
                days_silent=round(features.days_since_last_activity, 2),
                step_key=features.current_step_key,
            )
            opened += 1
        elif not is_silent and existing is not None:
            await signal_repo.close(existing, returned_at=now)

    return opened
