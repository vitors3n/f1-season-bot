from config import WEB_APP_URL
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
    WebAppInfo,
)
from telegram.ext import ContextTypes


MENSAGEM_DASHBOARD = "🏎️ <b>Dashboard da F1</b>\n\nAcompanhe o próximo GP e a programação do fim de semana."
MENSAGEM_DASHBOARD_INDISPONIVEL = "⚠️ O dashboard ainda não está configurado."
BOTAO_PROXIMO_GP = "🏁 Próximo GP"
BOTAO_COUNTDOWN = "⏳ Contagem regressiva"


def teclado_dashboard(chat_type):
    if chat_type == "private":
        botoes = []
        if WEB_APP_URL:
            botoes.append([KeyboardButton("🏎️ Abrir dashboard", web_app=WebAppInfo(WEB_APP_URL))])
        botoes.append([KeyboardButton(BOTAO_PROXIMO_GP), KeyboardButton(BOTAO_COUNTDOWN)])
        return ReplyKeyboardMarkup(
            botoes,
            resize_keyboard=True,
        )
    if not WEB_APP_URL:
        return None
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🏎️ Abrir dashboard", url=WEB_APP_URL)]]
    )


async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not WEB_APP_URL:
        await update.message.reply_text(MENSAGEM_DASHBOARD_INDISPONIVEL)
        return
    await update.message.reply_text(
        MENSAGEM_DASHBOARD,
        parse_mode="HTML",
        reply_markup=teclado_dashboard(update.effective_chat.type),
    )
