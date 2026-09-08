from comandos.mensagens import ERRO_CONSULTA, proxima_corrida
from servicos.pega_corrida import pega_corrida
from telegram.ext import ContextTypes
from telegram import Update


async def next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    corrida = await pega_corrida()
    if corrida is None:
        await update.message.reply_text(ERRO_CONSULTA)
        return
    await update.message.reply_text(proxima_corrida(corrida), parse_mode='HTML')
