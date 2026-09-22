from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from comandos.mensagens import configuracoes_chat
from servicos.configuracoes import (
    ANTECEDENCIAS_DISPONIVEIS,
    SESSOES_PADRAO,
    alternar_antecedencia,
    alternar_sessao,
    obter_configuracoes,
    restaurar_configuracoes,
)
from servicos.permissoes import exigir_administrador


NOMES_SESSOES = {
    "fp1": "TL1", "fp2": "TL2", "fp3": "TL3", "sprint_quali": "Quali Sprint",
    "sprint": "Sprint", "quali": "Classificação", "race": "Corrida",
}


def _teclado(configuracoes, tela="inicio"):
    if tela == "sessoes":
        botoes = [
            [InlineKeyboardButton(
                f"{'✅' if sessao in configuracoes['sessions'] else '⬜'} {NOMES_SESSOES[sessao]}",
                callback_data=f"settings:toggle:{sessao}",
            )]
            for sessao in SESSOES_PADRAO
        ]
        botoes.append([InlineKeyboardButton("‹ Voltar", callback_data="settings:home")])
        return InlineKeyboardMarkup(botoes)

    if tela == "antecedencias":
        botoes = [
            [InlineKeyboardButton(
                f"{'✅' if minutos in configuracoes['reminder_minutes'] else '⬜'} {minutos} min antes",
                callback_data=f"settings:toggle_reminder:{minutos}",
            )]
            for minutos in ANTECEDENCIAS_DISPONIVEIS
        ]
        botoes.append([InlineKeyboardButton("‹ Voltar", callback_data="settings:home")])
        return InlineKeyboardMarkup(botoes)

    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏁 Sessões dos lembretes", callback_data="settings:sessions")],
        [InlineKeyboardButton("⏰ Antecedência dos lembretes", callback_data="settings:reminders")],
        [InlineKeyboardButton("↩️ Restaurar padrão", callback_data="settings:reset")],
    ])


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await exigir_administrador(update, context):
        return

    configuracoes = obter_configuracoes(update.effective_chat.id)
    await update.message.reply_text(
        configuracoes_chat(configuracoes), parse_mode="HTML", reply_markup=_teclado(configuracoes)
    )


async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not await exigir_administrador(update, context):
        return

    await query.answer()
    chat_id = update.effective_chat.id
    acao, *argumentos = query.data.split(":")[1:]

    if acao == "toggle":
        configuracoes = alternar_sessao(chat_id, argumentos[0])
        await query.edit_message_text(
            configuracoes_chat(configuracoes, tela="sessoes"),
            parse_mode="HTML", reply_markup=_teclado(configuracoes, tela="sessoes"),
        )
        return

    if acao == "toggle_reminder":
        configuracoes = alternar_antecedencia(chat_id, int(argumentos[0]))
        await query.edit_message_text(
            configuracoes_chat(configuracoes, tela="antecedencias"),
            parse_mode="HTML", reply_markup=_teclado(configuracoes, tela="antecedencias"),
        )
        return

    if acao == "reset":
        configuracoes = restaurar_configuracoes(chat_id)
    else:
        configuracoes = obter_configuracoes(chat_id)

    tela = "sessoes" if acao == "sessions" else "antecedencias" if acao == "reminders" else "inicio"
    await query.edit_message_text(
        configuracoes_chat(configuracoes, tela=tela),
        parse_mode="HTML", reply_markup=_teclado(configuracoes, tela=tela),
    )
