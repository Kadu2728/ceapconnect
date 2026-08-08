"""Seed idempotente dos catálogos do Dashboard (EPIC 03).

Popula `JourneyStep`, `Mission`, `Achievement` e `Event` com dados
representativos, caso ainda não existam — nunca duplica em reexecuções
(cada catálogo é checado por sua chave natural: `key`/`title`/`name`).

Uso:
    python -m app.core.seed

Não é uma migration: migrations do Alembic cuidam apenas do *schema*
(estrutura das tabelas); este script cuida dos *dados* de catálogo, que
podem evoluir de forma independente do schema (ex.: adicionar uma nova
missão não exige alterar nenhuma coluna).
"""

import asyncio
import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, engine
from app.models.achievement import Achievement
from app.models.candidate_profile import CandidateProfile
from app.models.cohort import Cohort
from app.models.event import Event
from app.models.journey_step import JourneyStep
from app.models.mission import Mission
from app.models.reward import Reward
from app.models.simulado import SUBJECT_MATEMATICA, SUBJECT_PORTUGUES, SimuladoQuestion

logger = logging.getLogger("ceap_connect.seed")
logging.basicConfig(level=logging.INFO)

_JOURNEY_STEPS: tuple[dict, ...] = (
    {
        "key": "inscricao",
        "label": "Inscrição",
        "description": "Cadastro realizado e conta criada na plataforma.",
        "order": 1,
    },
    {
        "key": "documentacao",
        "label": "Documentação",
        "description": "Envio e validação dos documentos exigidos no edital.",
        "order": 2,
    },
    {
        "key": "confirmacao",
        "label": "Confirmação",
        "description": "Inscrição confirmada após validação da documentação.",
        "order": 3,
    },
    {
        "key": "preparacao",
        "label": "Preparação",
        "description": "Período de estudos e acompanhamento das missões e eventos.",
        "order": 4,
    },
    {
        "key": "dia_da_prova",
        "label": "Dia da prova",
        "description": "Realização da prova do processo seletivo.",
        "order": 5,
    },
    {
        "key": "resultado",
        "label": "Resultado",
        "description": "Divulgação do resultado final do processo seletivo.",
        "order": 6,
    },
)

_MISSIONS: tuple[dict, ...] = (
    {
        "title": "Conheça o CEAP",
        "description": "Explore a plataforma e conheça a estrutura do CEAP Connect.",
        "xp_reward": 20,
        "due_date": None,
    },
    {
        "title": "Assista ao vídeo institucional",
        "description": "Assista ao vídeo de apresentação do processo seletivo.",
        "xp_reward": 30,
        "due_date": None,
    },
    {
        "title": "Confirme sua documentação",
        "description": "Envie e confirme os documentos exigidos no edital.",
        "xp_reward": 50,
        "due_date": None,
    },
    {
        "title": "Responda o quiz de ambientação",
        "description": "Responda o quiz rápido sobre como funciona a jornada.",
        "xp_reward": 25,
        "due_date": None,
    },
)

_ACHIEVEMENTS: tuple[dict, ...] = (
    {
        "name": "Primeira Missão",
        "description": "Concluiu a primeira missão da jornada.",
        "icon": "flag",
    },
    {
        "name": "100 XP",
        "description": "Acumulou 100 pontos de experiência.",
        "icon": "zap",
    },
    {
        "name": "Perfil Completo",
        "description": "Completou 100% dos dados do perfil.",
        "icon": "badge-check",
    },
)


# Recompensas reais (cursos/certificações externas). As duas primeiras são
# desbloqueadas por CONQUISTA (o "conclua a conquista → ganhe o curso" pedido
# pela direção); as demais, por NÍVEL. `required_achievement_name` é resolvido
# para o id da conquista no momento do seed. Ajuste esta lista para o que o CEAP
# de fato oferecer — desativar sem apagar: `is_active=False`.
_REWARDS: tuple[dict, ...] = (
    {
        "title": "Pacote Office na prática",
        "description": (
            "Curso completo de Word, Excel e PowerPoint para dar seus primeiros "
            "passos no mundo profissional — 100% gratuito e com certificado."
        ),
        "provider": "Fundação Bradesco",
        "category": "Curso",
        "icon": "monitor",
        "unlock_type": "achievement",
        "required_achievement_name": "Primeira Missão",
        "required_level": None,
        "featured": True,
        "sort_order": 1,
    },
    {
        "title": "AWS Cloud Practitioner",
        "description": (
            "Trilha oficial + voucher de certificação em computação em nuvem da "
            "Amazon — uma das credenciais mais valorizadas do mercado de tecnologia."
        ),
        "provider": "Amazon Web Services",
        "category": "Certificação",
        "icon": "cloud",
        "unlock_type": "achievement",
        "required_achievement_name": "100 XP",
        "required_level": None,
        "featured": True,
        "sort_order": 2,
    },
    {
        "title": "Edição de Vídeo e Audiovisual",
        "description": (
            "Curso prático de captação e edição de vídeo — a base da formação em "
            "Cinema e Audiovisual do CEAP."
        ),
        "provider": "Fundação Bradesco",
        "category": "Curso",
        "icon": "clapperboard",
        "unlock_type": "level",
        "required_achievement_name": None,
        "required_level": 2,
        "featured": False,
        "sort_order": 3,
    },
    {
        "title": "Excel Avançado para Administração",
        "description": (
            "Domine planilhas, dashboards e automações que fazem a diferença na "
            "área administrativa e financeira."
        ),
        "provider": "Fundação Bradesco",
        "category": "Curso",
        "icon": "table",
        "unlock_type": "level",
        "required_achievement_name": None,
        "required_level": 3,
        "featured": False,
        "sort_order": 4,
    },
    {
        "title": "Google IT Support Professional",
        "description": (
            "Certificado profissional de suporte em TI do Google, reconhecido "
            "internacionalmente — porta de entrada para a área de Informática."
        ),
        "provider": "Google",
        "category": "Certificação",
        "icon": "badge-check",
        "unlock_type": "level",
        "required_achievement_name": None,
        "required_level": 3,
        "featured": False,
        "sort_order": 5,
    },
    {
        "title": "Fundamentos de Redes (CCNA Intro)",
        "description": (
            "Curso oficial da Cisco sobre fundamentos de redes de computadores — "
            "teoria e prática que o mercado de Redes exige."
        ),
        "provider": "Cisco Networking Academy",
        "category": "Curso",
        "icon": "network",
        "unlock_type": "level",
        "required_achievement_name": None,
        "required_level": 4,
        "featured": False,
        "sort_order": 6,
    },
    {
        "title": "Certificação de Inglês EF SET",
        "description": (
            "Teste e certificado de proficiência em inglês reconhecido mundialmente "
            "— um diferencial em qualquer carreira."
        ),
        "provider": "EF Education First",
        "category": "Certificação",
        "icon": "languages",
        "unlock_type": "level",
        "required_achievement_name": None,
        "required_level": 5,
        "featured": False,
        "sort_order": 7,
    },
)


# Banco de questões dos Simulados (EPIC 16), no formato real da prova do CEAP
# (Português + Matemática, múltipla escolha). `statement` é a chave natural do
# seed — editar o texto de uma questão existente cria uma nova em vez de
# atualizar (mesma limitação simples do resto dos catálogos deste arquivo).
_SIMULADO_QUESTIONS: tuple[dict, ...] = (
    # --- Português ---
    {
        "subject": SUBJECT_PORTUGUES,
        "statement": "Assinale a alternativa com a grafia correta:",
        "options": [
            {"key": "a", "text": "Excessão"},
            {"key": "b", "text": "Exceção"},
            {"key": "c", "text": "Ecessão"},
            {"key": "d", "text": "Excessao"},
        ],
        "correct_option_key": "b",
        "explanation": '"Exceção" se escreve com "ç" e apenas um "s".',
    },
    {
        "subject": SUBJECT_PORTUGUES,
        "statement": '"Os alunos ___ para a prova." Complete corretamente:',
        "options": [
            {"key": "a", "text": "se preparou"},
            {"key": "b", "text": "se prepararam"},
            {"key": "c", "text": "se preparam-se"},
            {"key": "d", "text": "se preparado"},
        ],
        "correct_option_key": "b",
        "explanation": 'O sujeito "os alunos" está no plural, então o verbo também deve estar.',
    },
    {
        "subject": SUBJECT_PORTUGUES,
        "statement": (
            'Texto: "Ana chegou cedo à escola, mas a prova só começaria às 9h. Por isso, '
            'ela aproveitou para revisar o conteúdo." Por que Ana revisou o conteúdo?'
        ),
        "options": [
            {"key": "a", "text": "Porque a prova havia sido cancelada"},
            {"key": "b", "text": "Porque ela chegou atrasada"},
            {"key": "c", "text": "Porque sobrou tempo antes do início da prova"},
            {"key": "d", "text": "Porque o professor pediu"},
        ],
        "correct_option_key": "c",
        "explanation": (
            'O texto diz que ela chegou cedo e a prova "só começaria às 9h", ou seja, sobrou tempo.'
        ),
    },
    {
        "subject": SUBJECT_PORTUGUES,
        "statement": (
            'Na frase "Ela estudou muito para a prova", a palavra "muito" classifica-se como:'
        ),
        "options": [
            {"key": "a", "text": "substantivo"},
            {"key": "b", "text": "advérbio"},
            {"key": "c", "text": "preposição"},
            {"key": "d", "text": "conjunção"},
        ],
        "correct_option_key": "b",
        "explanation": (
            '"Muito" modifica o verbo "estudou", indicando intensidade — função de advérbio.'
        ),
    },
    {
        "subject": SUBJECT_PORTUGUES,
        "statement": "Assinale a palavra acentuada corretamente:",
        "options": [
            {"key": "a", "text": "Ambulância"},
            {"key": "b", "text": "Ambulancia"},
            {"key": "c", "text": "Ambulánci"},
            {"key": "d", "text": "Anbulância"},
        ],
        "correct_option_key": "a",
        "explanation": '"Ambulância" é uma palavra proparoxítona — todas são acentuadas.',
    },
    {
        "subject": SUBJECT_PORTUGUES,
        "statement": 'Um sinônimo adequado para "árduo" (como em "um trabalho árduo") é:',
        "options": [
            {"key": "a", "text": "fácil"},
            {"key": "b", "text": "difícil"},
            {"key": "c", "text": "rápido"},
            {"key": "d", "text": "alegre"},
        ],
        "correct_option_key": "b",
        "explanation": '"Árduo" significa trabalhoso, custoso — sinônimo de "difícil".',
    },
    {
        "subject": SUBJECT_PORTUGUES,
        "statement": "Assinale a frase com a concordância correta:",
        "options": [
            {"key": "a", "text": "As meninas está feliz"},
            {"key": "b", "text": "As meninas estão felizes"},
            {"key": "c", "text": "As menina estão feliz"},
            {"key": "d", "text": "As meninas estão feliz"},
        ],
        "correct_option_key": "b",
        "explanation": (
            'Sujeito e predicativo concordam em número: "as meninas" (plural) → '
            '"estão felizes" (plural).'
        ),
    },
    {
        "subject": SUBJECT_PORTUGUES,
        "statement": "Assinale a frase com a pontuação correta:",
        "options": [
            {"key": "a", "text": "Maria, você viu o João?"},
            {"key": "b", "text": "Maria você, viu o João?"},
            {"key": "c", "text": "Maria você viu, o João?"},
            {"key": "d", "text": "Maria você viu o João"},
        ],
        "correct_option_key": "a",
        "explanation": (
            'A vírgula separa o vocativo ("Maria") do restante da frase, e a '
            "interrogação fecha a pergunta."
        ),
    },
    {
        "subject": SUBJECT_PORTUGUES,
        "statement": (
            '"Depois de muito esforço, Pedro finalmente conseguiu a vaga." '
            "O trecho sugere que Pedro:"
        ),
        "options": [
            {"key": "a", "text": "desistiu no meio do caminho"},
            {"key": "b", "text": "conseguiu a vaga facilmente"},
            {"key": "c", "text": "se esforçou até alcançar seu objetivo"},
            {"key": "d", "text": "não conseguiu a vaga"},
        ],
        "correct_option_key": "c",
        "explanation": (
            '"Depois de muito esforço... finalmente conseguiu" indica persistência até o resultado.'
        ),
    },
    {
        "subject": SUBJECT_PORTUGUES,
        "statement": 'O antônimo de "generoso" é:',
        "options": [
            {"key": "a", "text": "gentil"},
            {"key": "b", "text": "mesquinho"},
            {"key": "c", "text": "alegre"},
            {"key": "d", "text": "educado"},
        ],
        "correct_option_key": "b",
        "explanation": '"Mesquinho" (avarento, egoísta) é o oposto de "generoso".',
    },
    {
        "subject": SUBJECT_PORTUGUES,
        "statement": "Assinale a alternativa que segue a norma culta:",
        "options": [
            {"key": "a", "text": "Assisti o filme ontem"},
            {"key": "b", "text": "Assisti ao filme ontem"},
            {"key": "c", "text": "Assisti no filme ontem"},
            {"key": "d", "text": "Assisti de filme ontem"},
        ],
        "correct_option_key": "b",
        "explanation": (
            'No sentido de "ver", o verbo "assistir" pede a preposição "a": "assisti ao filme".'
        ),
    },
    {
        "subject": SUBJECT_PORTUGUES,
        "statement": (
            'Qual é a ideia central da frase: "A leitura amplia o vocabulário e melhora a escrita"?'
        ),
        "options": [
            {"key": "a", "text": "Ler não influencia a escrita"},
            {"key": "b", "text": "A leitura traz benefícios para a linguagem"},
            {"key": "c", "text": "Escrever é mais importante que ler"},
            {"key": "d", "text": "O vocabulário não depende da leitura"},
        ],
        "correct_option_key": "b",
        "explanation": "A frase relaciona diretamente ler com ganhos de vocabulário e escrita.",
    },
    # --- Matemática ---
    {
        "subject": SUBJECT_MATEMATICA,
        "statement": "Quanto é 15% de 200?",
        "options": [
            {"key": "a", "text": "20"},
            {"key": "b", "text": "30"},
            {"key": "c", "text": "15"},
            {"key": "d", "text": "40"},
        ],
        "correct_option_key": "b",
        "explanation": "200 × 0,15 = 30.",
    },
    {
        "subject": SUBJECT_MATEMATICA,
        "statement": "Simplifique a fração 8/12:",
        "options": [
            {"key": "a", "text": "2/3"},
            {"key": "b", "text": "4/6"},
            {"key": "c", "text": "3/4"},
            {"key": "d", "text": "1/2"},
        ],
        "correct_option_key": "a",
        "explanation": "Dividindo numerador e denominador por 4: 8/12 = 2/3.",
    },
    {
        "subject": SUBJECT_MATEMATICA,
        "statement": "Um produto custava R$ 50 e teve um desconto de 10%. Qual o novo preço?",
        "options": [
            {"key": "a", "text": "R$ 40"},
            {"key": "b", "text": "R$ 45"},
            {"key": "c", "text": "R$ 48"},
            {"key": "d", "text": "R$ 55"},
        ],
        "correct_option_key": "b",
        "explanation": "10% de 50 é 5. 50 - 5 = 45.",
    },
    {
        "subject": SUBJECT_MATEMATICA,
        "statement": "Resolva: 3x + 5 = 20. Qual o valor de x?",
        "options": [
            {"key": "a", "text": "3"},
            {"key": "b", "text": "5"},
            {"key": "c", "text": "15"},
            {"key": "d", "text": "25"},
        ],
        "correct_option_key": "b",
        "explanation": "3x = 20 - 5 = 15, logo x = 15 ÷ 3 = 5.",
    },
    {
        "subject": SUBJECT_MATEMATICA,
        "statement": (
            "Uma receita rende 4 bolos com 2kg de farinha. Quantos kg de farinha são "
            "necessários para fazer 6 bolos, mantendo a mesma proporção?"
        ),
        "options": [
            {"key": "a", "text": "2kg"},
            {"key": "b", "text": "3kg"},
            {"key": "c", "text": "4kg"},
            {"key": "d", "text": "6kg"},
        ],
        "correct_option_key": "b",
        "explanation": "Regra de três: 2/4 = x/6 → x = (2 × 6) ÷ 4 = 3kg.",
    },
    {
        "subject": SUBJECT_MATEMATICA,
        "statement": "Qual é o resultado de 7² - 4²?",
        "options": [
            {"key": "a", "text": "9"},
            {"key": "b", "text": "33"},
            {"key": "c", "text": "49"},
            {"key": "d", "text": "65"},
        ],
        "correct_option_key": "b",
        "explanation": "7² = 49 e 4² = 16. 49 - 16 = 33.",
    },
    {
        "subject": SUBJECT_MATEMATICA,
        "statement": "Quanto é 2/5 + 1/5?",
        "options": [
            {"key": "a", "text": "3/10"},
            {"key": "b", "text": "3/5"},
            {"key": "c", "text": "1/5"},
            {"key": "d", "text": "2/25"},
        ],
        "correct_option_key": "b",
        "explanation": "Frações de mesmo denominador: soma-se apenas o numerador. 2/5 + 1/5 = 3/5.",
    },
    {
        "subject": SUBJECT_MATEMATICA,
        "statement": (
            "Um carro percorre 60km em 1 hora. Mantendo a mesma velocidade, quantos km "
            "percorrerá em 3 horas?"
        ),
        "options": [
            {"key": "a", "text": "120km"},
            {"key": "b", "text": "150km"},
            {"key": "c", "text": "180km"},
            {"key": "d", "text": "200km"},
        ],
        "correct_option_key": "c",
        "explanation": "60km/h × 3h = 180km.",
    },
    {
        "subject": SUBJECT_MATEMATICA,
        "statement": "Qual é o perímetro de um quadrado com lado de 5cm?",
        "options": [
            {"key": "a", "text": "10cm"},
            {"key": "b", "text": "15cm"},
            {"key": "c", "text": "20cm"},
            {"key": "d", "text": "25cm"},
        ],
        "correct_option_key": "c",
        "explanation": "O perímetro do quadrado é 4 × lado = 4 × 5 = 20cm.",
    },
    {
        "subject": SUBJECT_MATEMATICA,
        "statement": "Converta 0,75 em fração:",
        "options": [
            {"key": "a", "text": "3/4"},
            {"key": "b", "text": "7/5"},
            {"key": "c", "text": "75/1000"},
            {"key": "d", "text": "1/4"},
        ],
        "correct_option_key": "a",
        "explanation": "0,75 = 75/100, que simplificado dá 3/4.",
    },
    {
        "subject": SUBJECT_MATEMATICA,
        "statement": (
            "Se 5 trabalhadores fazem um serviço em 12 dias, quantos dias levariam 10 "
            "trabalhadores para fazer o mesmo serviço, mantendo a mesma produtividade?"
        ),
        "options": [
            {"key": "a", "text": "24 dias"},
            {"key": "b", "text": "12 dias"},
            {"key": "c", "text": "6 dias"},
            {"key": "d", "text": "3 dias"},
        ],
        "correct_option_key": "c",
        "explanation": "Regra de três inversa: 5 × 12 = 10 × x → x = 60 ÷ 10 = 6 dias.",
    },
    {
        "subject": SUBJECT_MATEMATICA,
        "statement": "Qual o valor de 100 ÷ 4 × 2?",
        "options": [
            {"key": "a", "text": "12,5"},
            {"key": "b", "text": "50"},
            {"key": "c", "text": "25"},
            {"key": "d", "text": "200"},
        ],
        "correct_option_key": "b",
        "explanation": (
            "Divisão e multiplicação têm a mesma prioridade e se resolvem da esquerda "
            "para a direita: 100 ÷ 4 = 25, depois 25 × 2 = 50."
        ),
    },
)


def _future_events(now: datetime) -> tuple[dict, ...]:
    """Monta os eventos de seed com datas relativas a `now` (sempre futuras)."""
    return (
        {
            "title": "Palestra: Como se preparar para a prova do CEAP",
            "description": "Dicas práticas de estudo e gestão do tempo com especialistas do CEAP.",
            "date": now + timedelta(days=14),
            "location": "Auditório Central do CEAP",
            "image_url": None,
        },
        {
            "title": "Encontro de boas-vindas dos candidatos",
            "description": "Roda de conversa para os candidatos se conhecerem e tirarem dúvidas.",
            "date": now + timedelta(days=21),
            "location": "Online — transmissão ao vivo",
            "image_url": None,
        },
        {
            "title": "Simulado presencial CEAP Connect",
            "description": "Simulado completo nas mesmas condições do dia da prova oficial.",
            "date": now + timedelta(days=45),
            "location": "Unidade CEAP — Sede",
            "image_url": None,
        },
    )


async def _seed_journey_steps(db: AsyncSession) -> int:
    existing = {row.key for row in (await db.execute(select(JourneyStep.key))).all()}
    to_create = [JourneyStep(**data) for data in _JOURNEY_STEPS if data["key"] not in existing]
    db.add_all(to_create)
    return len(to_create)


async def _seed_missions(db: AsyncSession) -> int:
    existing = {row.title for row in (await db.execute(select(Mission.title))).all()}
    to_create = [Mission(**data) for data in _MISSIONS if data["title"] not in existing]
    db.add_all(to_create)
    return len(to_create)


async def _seed_achievements(db: AsyncSession) -> int:
    existing = {row.name for row in (await db.execute(select(Achievement.name))).all()}
    to_create = [Achievement(**data) for data in _ACHIEVEMENTS if data["name"] not in existing]
    db.add_all(to_create)
    return len(to_create)


async def _seed_events(db: AsyncSession) -> int:
    existing = {row.title for row in (await db.execute(select(Event.title))).all()}
    to_create = [
        Event(**data) for data in _future_events(datetime.now(UTC)) if data["title"] not in existing
    ]
    db.add_all(to_create)
    return len(to_create)


async def _seed_cohort(db: AsyncSession) -> tuple[int, int]:
    """Garante uma coorte para o período atual e atribui candidatos sem coorte.

    Idempotente pela chave natural (ano, semestre). O backfill só toca perfis
    com `cohort_id` nulo — candidatos já atribuídos nunca são movidos.

    Retorna (coortes criadas, perfis atribuídos).
    """
    now = datetime.now(UTC)
    year = now.year
    term = "1" if now.month <= 6 else "2"

    existing = (
        await db.execute(select(Cohort).where(Cohort.year == year, Cohort.term == term))
    ).scalar_one_or_none()

    created = 0
    if existing is None:
        existing = Cohort(
            name=f"Processo Seletivo {year}.{term}",
            year=year,
            term=term,
            is_active=True,
        )
        db.add(existing)
        await db.flush()
        created = 1

    result = await db.execute(
        update(CandidateProfile)
        .where(CandidateProfile.cohort_id.is_(None))
        .values(cohort_id=existing.id)
    )
    return created, result.rowcount or 0


async def _seed_rewards(db: AsyncSession) -> int:
    """Semeia as recompensas, resolvendo a conquista de gatilho pelo nome.

    Depende das conquistas já persistidas: `seed()` faz `flush()` após semear o
    catálogo de conquistas para que os ids estejam disponíveis aqui.
    """
    existing = {row.title for row in (await db.execute(select(Reward.title))).all()}
    achievements_by_name = {
        achievement.name: achievement.id
        for achievement in (await db.execute(select(Achievement))).scalars().all()
    }

    to_create: list[Reward] = []
    for data in _REWARDS:
        if data["title"] in existing:
            continue
        payload = {key: value for key, value in data.items() if key != "required_achievement_name"}
        achievement_name = data["required_achievement_name"]
        payload["required_achievement_id"] = (
            achievements_by_name.get(achievement_name) if achievement_name else None
        )
        to_create.append(Reward(**payload))

    db.add_all(to_create)
    return len(to_create)


async def _seed_simulado_questions(db: AsyncSession) -> int:
    existing = {
        row.statement for row in (await db.execute(select(SimuladoQuestion.statement))).all()
    }
    to_create = [
        SimuladoQuestion(**data)
        for data in _SIMULADO_QUESTIONS
        if data["statement"] not in existing
    ]
    db.add_all(to_create)
    return len(to_create)


async def seed() -> None:
    """Executa o seed completo, numa única transação idempotente."""
    async with AsyncSessionLocal() as db:
        created_steps = await _seed_journey_steps(db)
        created_missions = await _seed_missions(db)
        created_achievements = await _seed_achievements(db)
        # Recompensas resolvem a conquista de gatilho pelo id: garante que as
        # conquistas recém-criadas já tenham id antes de semear as recompensas.
        await db.flush()
        created_events = await _seed_events(db)
        created_rewards = await _seed_rewards(db)
        created_cohorts, assigned_profiles = await _seed_cohort(db)
        created_questions = await _seed_simulado_questions(db)
        await db.commit()

    logger.info(
        "Seed concluído: %d etapas, %d missões, %d conquistas, %d eventos, "
        "%d recompensas, %d coorte(s) criadas, %d candidato(s) atribuídos à coorte, "
        "%d questão(ões) de simulado.",
        created_steps,
        created_missions,
        created_achievements,
        created_events,
        created_rewards,
        created_cohorts,
        assigned_profiles,
        created_questions,
    )


async def _main() -> None:
    try:
        await seed()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(_main())
