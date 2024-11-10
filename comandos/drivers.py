from utils.campeonato_pilotos import campeonato_pilotos
from telegram.ext import ContextTypes
from telegram import Update

async def drivers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pilotos = campeonato_pilotos()

    message = "<b>Campeonato de Pilotos</b>\n"
    for piloto in pilotos:
        print(piloto)
        message += f"<b>{ piloto['position'] } - { piloto['Driver']['givenName'] } { piloto['Driver']['familyName'] } - { piloto['points'] } </b>\n"

    await update.message.reply_text(message, parse_mode='HTML')
