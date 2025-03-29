from utils.campeonato_construtores import campeonato_construtores
from telegram.ext import ContextTypes
from telegram import Update

async def teams(update: Update, context: ContextTypes.DEFAULT_TYPE):
    times = campeonato_construtores()
    ano_atual = datetime.now().year

    message = f"<b>Campeonato de Construtores - {ano_atual}</b>\n"
    for time in times:
        nome_time = f"{ time['Constructor']['name'] } "
        message += f"{ time['position'] } - { nome_time } - { time['points'] }\n"

    await update.message.reply_text(message, parse_mode='HTML')
