"""prune extra simulado questions (60 -> 30 no banco)

Revision ID: d2e3f4a5b6c7
Revises: c1d2e3f4a5b6
Create Date: 2026-08-25 00:00:00.000000

O banco de questões foi ampliado de 24 para 60 (12 -> 30 por matéria) numa
migration de dados anterior (fora do Alembic — via seed idempotente,
`app.core.seed`). O usuário decidiu que 60 é demais; esta migration remove
as 30 questões extras (mantendo as 12 originais + 3 das novas por matéria =
15+15=30), a mesma lista que `app.core.seed._SIMULADO_QUESTIONS` deixou de
conter.

**Guardada por segurança**: só apaga uma questão se `NOT EXISTS` nenhuma
`simulado_answers` referenciando ela — nunca remove uma questão que algum
candidato já respondeu (evitaria cascatear a exclusão para a resposta dele,
corrompendo o resultado histórico da tentativa). Dado o pouco tempo entre a
inserção das 36 questões novas e esta migration, nenhuma delas deveria ter
resposta ainda — mas a guarda torna isso uma garantia, não uma suposição.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "d2e3f4a5b6c7"
down_revision: str | None = "c1d2e3f4a5b6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_STATEMENTS_TO_REMOVE: tuple[str, ...] = (
    # --- Português (12 das 18 adicionadas) ---
    "Assinale a frase com a vírgula usada corretamente:",
    (
        'Texto: "Marcos estudou todos os dias durante um mês para o processo '
        'seletivo do CEAP e, na véspera da prova, decidiu descansar." Por que '
        "Marcos descansou na véspera da prova?"
    ),
    'Em "Chorei rios de lágrimas", a figura de linguagem usada é:',
    (
        'Em "O menino, que é muito esperto, resolveu o problema rápido", o trecho '
        '"que é muito esperto" é uma oração subordinada:'
    ),
    'Um sinônimo adequado para "árido" (como em "terreno árido") é:',
    "Assinale a frase de acordo com a norma culta:",
    'Complete: "Ele tem aptidão ___ matemática."',
    '"O livro foi lido pelo aluno" está na voz:',
    'Em "A mãe da menina que estava doente chegou", quem estava doente?',
    'Complete conforme a concordância: "Seguem ___ os documentos."',
    'Um sinônimo adequado para "efêmero" é:',
    'Em "Ele tem um coração de pedra", o sentido da expressão é:',
    "Assinale a alternativa com a acentuação correta:",
    'Complete: "A ___ de cinema começa às 20h."',
    (
        'Texto: "O CEAP oferece cursos técnicos gratuitos para jovens, com o '
        'objetivo de ampliar o acesso à educação profissional." Segundo o texto, '
        "qual é o objetivo do CEAP?"
    ),
    # --- Matemática (12 das 18 adicionadas) ---
    "Qual é o MMC (mínimo múltiplo comum) entre 4 e 6?",
    "Um caminhão percorre 300km com 25 litros de combustível. Qual o consumo médio, em km/l?",
    "Qual é a área de um retângulo com base 8cm e altura 5cm?",
    "Converta a fração 3/8 em número decimal:",
    "Um produto de R$ 120 sofre um aumento de 25%. Qual o novo preço?",
    "Qual é o resultado de (-3) + 5 - 8?",
    "Numa turma de 40 alunos, 60% são meninas. Quantos meninos há?",
    "Qual é o valor de 2³ + 3²?",
    "A razão entre dois números é 3:5. Se o menor deles vale 12, quanto vale o maior?",
    "Qual é o próximo número da sequência: 2, 4, 8, 16, ...?",
    "Quanto é 1/2 + 1/3?",
    "Um terreno retangular mede 12m de comprimento por 8m de largura. Qual o seu perímetro?",
    (
        "Se 8 operários constroem um muro em 15 dias, quantos dias levariam 4 "
        "operários para construir o mesmo muro, no mesmo ritmo?"
    ),
    "Qual o valor de x na equação x/4 = 9?",
    "Numa pesquisa com 200 pessoas, 30% preferem o produto A. Quantas pessoas preferem o produto A?",
)


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "DELETE FROM simulado_questions "
            "WHERE statement = ANY(:statements) "
            "AND id NOT IN (SELECT DISTINCT question_id FROM simulado_answers)"
        ),
        {"statements": list(_STATEMENTS_TO_REMOVE)},
    )


def downgrade() -> None:
    # Dado apagado (conteúdo de catálogo, não estado de usuário) — reinserir
    # é responsabilidade do seed (`python -m app.core.seed` com a lista
    # antiga), não desta migration.
    pass
