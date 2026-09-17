import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import httpx

from comandos import calendar as comando_calendar
from comandos import drivers as comando_drivers
from comandos import next as comando_next
from comandos import qualifying as comando_qualifying
from comandos import teams as comando_teams
from comandos import weather as comando_weather
from comandos.mensagens import ERRO_CONSULTA
from servicos import http_client


def update_falso():
    return SimpleNamespace(
        message=SimpleNamespace(reply_text=AsyncMock()),
        effective_user=SimpleNamespace(id=123),
    )


class ApiIndisponivelTest(unittest.IsolatedAsyncioTestCase):
    async def test_comandos_exibem_erro_quando_api_indisponivel(self):
        cenarios = (
            (comando_next, "next", "pega_corrida"),
            (comando_calendar, "calendar", "pega_calendario"),
            (comando_qualifying, "qualifying", "pega_ultima_classificacao"),
            (comando_drivers, "drivers", "campeonato_pilotos"),
            (comando_teams, "teams", "campeonato_construtores"),
            (comando_weather, "weather", "pega_corrida"),
        )

        for modulo, handler, consulta in cenarios:
            with self.subTest(handler=handler):
                update = update_falso()
                with patch.object(modulo, consulta, new=AsyncMock(return_value=None)):
                    await getattr(modulo, handler)(update, None)

                update.message.reply_text.assert_awaited_once_with(ERRO_CONSULTA)

    async def test_callback_do_calendario_exibe_erro_quando_api_indisponivel(self):
        query = SimpleNamespace(
            data="calendar:2:123",
            from_user=SimpleNamespace(id=123),
            answer=AsyncMock(),
            edit_message_text=AsyncMock(),
        )
        update = SimpleNamespace(callback_query=query)

        with patch.object(comando_calendar, "pega_calendario", new=AsyncMock(return_value=None)):
            await comando_calendar.calendar_callback(update, None)

        query.answer.assert_awaited_once_with(ERRO_CONSULTA, show_alert=True)
        query.edit_message_text.assert_not_awaited()

    async def test_cliente_http_retorna_none_em_falha_de_conexao(self):
        cliente = SimpleNamespace(get=AsyncMock(side_effect=httpx.ConnectError("sem conexão")))

        with (
            patch.object(http_client, "iniciar_http_client", new=AsyncMock()),
            patch.object(http_client, "cliente_http", cliente),
        ):
            resposta = await http_client.busca_json("https://api.exemplo.test/dados")

        self.assertIsNone(resposta)

