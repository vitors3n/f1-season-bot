from telegram.constants import ChatMemberStatus, ChatType
from telegram.error import TelegramError

from comandos.mensagens import NAO_AUTORIZADO


async def pode_gerenciar_chat(update, context):
    chat = update.effective_chat
    if chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        return True

    try:
        membro = await context.bot.get_chat_member(chat.id, update.effective_user.id)
    except TelegramError:
        return False

    return membro.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)


async def exigir_administrador(update, context):
    if await pode_gerenciar_chat(update, context):
        return True

    if update.callback_query:
        await update.callback_query.answer(NAO_AUTORIZADO, show_alert=True)
    else:
        await update.effective_message.reply_text(NAO_AUTORIZADO)
    return False
