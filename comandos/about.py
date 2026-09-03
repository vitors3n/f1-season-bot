from comandos.mensagens import SOBRE_O_BOT
from telegram import Update
from telegram.ext import ContextTypes


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(SOBRE_O_BOT, parse_mode="HTML")
