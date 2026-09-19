import os
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

os.environ["BOT_TOKEN"] = os.getenv("BOT_TOKEN") or "123456:TESTE"

from comandos import notify as comando_notify
from comandos import settings as comando_settings
from comandos.mensagens import NAO_AUTORIZADO
from servicos import permissoes
from telegram.constants import ChatMemberStatus, ChatType
from telegram.error import TelegramError


def update_falso(tipo_chat=ChatType.GROUP):
    return SimpleNamespace(
        effective_chat=SimpleNamespace(id=-100, type=tipo_chat),
        effective_user=SimpleNamespace(id=123),
        effective_message=SimpleNamespace(reply_text=AsyncMock()),
        message=SimpleNamespace(reply_text=AsyncMock()),
        callback_query=None,
    )


class PermissoesTest(unittest.IsolatedAsyncioTestCase):
    async def test_conversa_privada_nao_consulta_permissao_e_permitida(self):
        update = update_falso(ChatType.PRIVATE)
        contexto = SimpleNamespace(bot=SimpleNamespace(get_chat_member=AsyncMock()))

        permitido = await permissoes.pode_gerenciar_chat(update, contexto)

        self.assertTrue(permitido)
        contexto.bot.get_chat_member.assert_not_awaited()

    async def test_administrador_e_dono_do_grupo_sao_permitidos(self):
        for status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            with self.subTest(status=status):
                update = update_falso()
                contexto = SimpleNamespace(
                    bot=SimpleNamespace(
                        get_chat_member=AsyncMock(return_value=SimpleNamespace(status=status))
                    )
                )

                permitido = await permissoes.pode_gerenciar_chat(update, contexto)

                self.assertTrue(permitido)

    async def test_membro_comum_do_grupo_nao_e_permitido(self):
        update = update_falso()
        contexto = SimpleNamespace(
            bot=SimpleNamespace(
                get_chat_member=AsyncMock(return_value=SimpleNamespace(status=ChatMemberStatus.MEMBER))
            )
        )

        permitido = await permissoes.pode_gerenciar_chat(update, contexto)

        self.assertFalse(permitido)

    async def test_falha_ao_consultar_telegram_bloqueia_por_seguranca(self):
        update = update_falso()
        contexto = SimpleNamespace(
            bot=SimpleNamespace(get_chat_member=AsyncMock(side_effect=TelegramError("falha")))
        )

        permitido = await permissoes.pode_gerenciar_chat(update, contexto)

        self.assertFalse(permitido)

    async def test_exigir_administrador_responde_erro_para_comando(self):
        update = update_falso()

        with patch.object(permissoes, "pode_gerenciar_chat", new=AsyncMock(return_value=False)):
            permitido = await permissoes.exigir_administrador(update, None)

        self.assertFalse(permitido)
        update.effective_message.reply_text.assert_awaited_once_with(NAO_AUTORIZADO)

    async def test_exigir_administrador_responde_alerta_para_botao(self):
        query = SimpleNamespace(answer=AsyncMock())
        update = update_falso()
        update.callback_query = query

        with patch.object(permissoes, "pode_gerenciar_chat", new=AsyncMock(return_value=False)):
            permitido = await permissoes.exigir_administrador(update, None)

        self.assertFalse(permitido)
        query.answer.assert_awaited_once_with(NAO_AUTORIZADO, show_alert=True)

    async def test_settings_bloqueado_nao_le_configuracoes(self):
        update = update_falso()

        with (
            patch.object(comando_settings, "exigir_administrador", new=AsyncMock(return_value=False)),
            patch.object(comando_settings, "obter_configuracoes") as obter_configuracoes,
        ):
            await comando_settings.settings(update, None)

        obter_configuracoes.assert_not_called()
        update.message.reply_text.assert_not_awaited()

    async def test_clear_notify_bloqueado_nao_remove_jobs(self):
        update = update_falso()
        scheduler = MagicMock()

        with (
            patch.object(comando_notify, "exigir_administrador", new=AsyncMock(return_value=False)),
            patch.object(comando_notify, "scheduler", scheduler),
        ):
            await comando_notify.clear_notify(update, None)

        scheduler.get_jobs.assert_not_called()
        update.message.reply_text.assert_not_awaited()

