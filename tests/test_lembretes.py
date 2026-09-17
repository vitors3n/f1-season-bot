import os
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

os.environ["BOT_TOKEN"] = os.getenv("BOT_TOKEN") or "123456:TESTE"

from comandos import notify as comando_notify
from comandos.mensagens import NOTIFICACOES_REMOVIDAS, lembrete
from modelos.corrida import Evento


def evento_com_horario():
    evento = Evento("2026-10-18", "15:00:00Z")
    evento.nome = "Classificação"
    return evento


def update_falso(chat_id=123):
    return SimpleNamespace(
        message=SimpleNamespace(
            chat=SimpleNamespace(id=chat_id),
            reply_text=AsyncMock(),
        ),
        effective_chat=SimpleNamespace(id=chat_id),
    )


class LembretesTest(unittest.IsolatedAsyncioTestCase):
    def test_agenda_um_job_por_antecedencia(self):
        evento = evento_com_horario()
        scheduler = MagicMock()

        with patch.object(comando_notify, "scheduler", scheduler):
            comando_notify.adiciona_lembrete(123, 456, evento, minutos_lembrete=(10, 5))

        self.assertEqual(scheduler.add_job.call_count, 2)
        chamadas = scheduler.add_job.call_args_list
        self.assertEqual(chamadas[0].kwargs["run_date"], evento.dia_hora_datetime() - comando_notify.timedelta(minutes=10))
        self.assertEqual(chamadas[1].kwargs["run_date"], evento.dia_hora_datetime() - comando_notify.timedelta(minutes=5))
        self.assertEqual(chamadas[0].kwargs["args"], [123, 456, "Classificação", 10])
        self.assertEqual(chamadas[1].kwargs["args"], [123, 456, "Classificação", 5])

    def test_nao_agenda_evento_sem_horario(self):
        evento = Evento("2026-10-18")
        evento.nome = "Corrida"
        scheduler = MagicMock()

        with patch.object(comando_notify, "scheduler", scheduler):
            comando_notify.adiciona_lembrete(123, None, evento)

        scheduler.add_job.assert_not_called()

    async def test_envia_mensagem_de_lembrete(self):
        bot = SimpleNamespace(send_message=AsyncMock())

        with patch.object(comando_notify, "bot", bot):
            await comando_notify.enviar_lembrete(123, 456, "Corrida", 10)

        bot.send_message.assert_awaited_once_with(
            chat_id=123,
            text=lembrete("Corrida", 10),
            parse_mode="HTML",
            reply_to_message_id=456,
        )

    async def test_clear_notify_remove_apenas_jobs_do_chat(self):
        update = update_falso(123)
        job_do_chat = MagicMock(args=[123, None])
        job_de_outro_chat = MagicMock(args=[456, None])
        scheduler = MagicMock()
        scheduler.get_jobs.return_value = [job_do_chat, job_de_outro_chat]

        with (
            patch.object(comando_notify, "scheduler", scheduler),
            patch.object(comando_notify, "exigir_administrador", new=AsyncMock(return_value=True)),
        ):
            await comando_notify.clear_notify(update, None)

        job_do_chat.remove.assert_called_once()
        job_de_outro_chat.remove.assert_not_called()
        update.message.reply_text.assert_awaited_once_with(NOTIFICACOES_REMOVIDAS)

    async def test_listnotify_lista_apenas_jobs_do_chat(self):
        update = update_falso(123)
        scheduler = MagicMock()
        scheduler.get_jobs.return_value = [
            SimpleNamespace(id="Corrida_Classificação_10min123"),
            SimpleNamespace(id="Corrida_Outro_10min456"),
        ]

        with patch.object(comando_notify, "scheduler", scheduler):
            await comando_notify.listnotify(update, None)

        texto = update.message.reply_text.await_args.args[0]
        self.assertIn("Classificação", texto)
        self.assertNotIn("Outro", texto)

