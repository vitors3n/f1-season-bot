from comandos.mensagens import ERRO_CONSULTA, calendario_temporada
from servicos.calendario import pega_calendario
from telegram import Update
from telegram.ext import ContextTypes


async def calendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    corridas = pega_calendario()
    if not corridas:
        await update.message.reply_text(ERRO_CONSULTA)
        return

    ano = corridas[0]["season"]
    await update.message.reply_text(
        calendario_temporada(corridas, ano),
        parse_mode="HTML",
    )
