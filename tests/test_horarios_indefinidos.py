import os
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

os.environ["BOT_TOKEN"] = os.getenv("BOT_TOKEN") or "123456:TESTE"

from comandos import countdown as comando_countdown
from comandos import notify as comando_notify
from comandos import weather as comando_weather
from comandos.mensagens import HORARIOS_INDEFINIDOS, proxima_corrida
from modelos.corrida import Corrida


def corrida_sem_horarios():
    return Corrida({
        "date": "2026-10-18",
        "raceName": "GP de Teste",
        "Circuit": {
            "circuitName": "Circuito de Teste",
            "Location": {"lat": "-3.0", "long": "-38.5"},
        },
        "FirstPractice": {"date": "2026-10-16"},
        "SecondPractice": {"date": "2026-10-16"},
        "ThirdPractice": {"date": "2026-10-17"},
        "Qualifying": {"date": "2026-10-17"},
    })


def update_falso():
    return SimpleNamespace(
        message=SimpleNamespace(
            chat=SimpleNamespace(id=123),
            message_thread_id=None,
            reply_text=AsyncMock(),
        ),
    )


class HorariosIndefinidosTest(unittest.IsolatedAsyncioTestCase):
    def test_modelo_aceita_sessoes_sem_time(self):
        corrida = corrida_sem_horarios()
        eventos = [corrida, corrida.fp1, corrida.fp2, corrida.fp3, corrida.quali]

        self.assertTrue(all(not evento.tem_horario for evento in eventos))
        self.assertTrue(all(evento.dia_hora_datetime() is None for evento in eventos))
        self.assertEqual(corrida.dia_hora(), "18/10/2026, horário a definir")

    def test_next_exibe_horario_a_definir(self):
        mensagem = proxima_corrida(corrida_sem_horarios())

        self.assertEqual(mensagem.count("horário a definir"), 5)

    async def test_countdown_informa_horarios_indefinidos(self):
        update = update_falso()
        with patch.object(comando_countdown, "pega_corrida", new=AsyncMock(return_value=corrida_sem_horarios())):
            await comando_countdown.countdown(update, None)

        update.message.reply_text.assert_awaited_once_with(HORARIOS_INDEFINIDOS)

    async def test_weather_nao_consulta_previsao_sem_horarios(self):
        update = update_falso()
        with (
            patch.object(comando_weather, "pega_corrida", new=AsyncMock(return_value=corrida_sem_horarios())),
            patch.object(comando_weather, "pega_previsao", new=AsyncMock()) as pega_previsao,
        ):
            await comando_weather.weather(update, None)

        pega_previsao.assert_not_awaited()
        update.message.reply_text.assert_awaited_once_with(HORARIOS_INDEFINIDOS)

    async def test_notify_nao_cria_lembretes_sem_horarios(self):
        update = update_falso()
        with (
            patch.object(comando_notify, "pega_corrida", new=AsyncMock(return_value=corrida_sem_horarios())),
            patch.object(comando_notify, "obter_configuracoes", return_value={"sessions": ("fp1", "fp2", "fp3", "quali", "race")}),
            patch.object(comando_notify, "adiciona_lembrete") as adiciona_lembrete,
        ):
            await comando_notify.notify(update, None)

        adiciona_lembrete.assert_not_called()
        update.message.reply_text.assert_awaited_once_with(HORARIOS_INDEFINIDOS)
