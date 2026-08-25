"""Testes de `app.core.reminder_rules` (lembretes automáticos).

Funções puras: sem I/O, sem banco.
"""

from app.core.reminder_rules import (
    should_remind_documentation_incomplete,
    should_remind_exam_1_day,
    should_remind_exam_7_days,
    should_remind_interview_1_day,
    should_remind_interview_7_days,
)


class TestExamReminders:
    def test_dentro_da_janela_de_7_dias(self) -> None:
        assert should_remind_exam_7_days(7) is True
        assert should_remind_exam_7_days(0) is True
        assert should_remind_exam_7_days(3) is True

    def test_fora_da_janela_de_7_dias(self) -> None:
        assert should_remind_exam_7_days(8) is False
        assert should_remind_exam_7_days(30) is False

    def test_prova_ja_passou_nao_dispara(self) -> None:
        assert should_remind_exam_7_days(-1) is False
        assert should_remind_exam_1_day(-1) is False

    def test_sem_data_de_prova_nao_dispara(self) -> None:
        assert should_remind_exam_7_days(None) is False
        assert should_remind_exam_1_day(None) is False

    def test_janela_de_1_dia_e_mais_estrita_que_a_de_7(self) -> None:
        assert should_remind_exam_1_day(1) is True
        assert should_remind_exam_1_day(2) is False


class TestInterviewReminders:
    def test_mesmo_comportamento_da_prova(self) -> None:
        assert should_remind_interview_7_days(7) is True
        assert should_remind_interview_7_days(8) is False
        assert should_remind_interview_1_day(0) is True
        assert should_remind_interview_1_day(2) is False
        assert should_remind_interview_7_days(None) is False


class TestDocumentationReminder:
    def test_dispara_apos_o_prazo_com_pendencia(self) -> None:
        assert (
            should_remind_documentation_incomplete(days_since_registration=5.0, pending_documents=1)
            is True
        )

    def test_nao_dispara_antes_do_prazo(self) -> None:
        assert (
            should_remind_documentation_incomplete(days_since_registration=4.9, pending_documents=1)
            is False
        )

    def test_nao_dispara_sem_pendencia_mesmo_apos_o_prazo(self) -> None:
        assert (
            should_remind_documentation_incomplete(
                days_since_registration=30.0, pending_documents=0
            )
            is False
        )
