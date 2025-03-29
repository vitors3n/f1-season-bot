from utils.campeonato_pilotos import campeonato_pilotos
from telegram.ext import ContextTypes
from telegram import Update

async def drivers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pilotos = campeonato_pilotos()

    print(pilotos)
    message = "<b>Campeonato de Pilotos</b>\n"

    ind = 1
    #piloto['position']
    for piloto in pilotos:
        nome_completo = f"{ piloto['Driver']['givenName'] } { piloto['Driver']['familyName'] }"
        message += f"{ ind } - { nome_completo } - { piloto['points'] }\n"
        ind = ind+1

    await update.message.reply_text(message, parse_mode='HTML')
