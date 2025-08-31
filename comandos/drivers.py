from utils.campeonato_pilotos import campeonato_pilotos
from telegram.ext import ContextTypes
from datetime import datetime
from telegram import Update

async def drivers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pilotos = campeonato_pilotos()
    
    if pilotos is None:
        await update.message.reply_text("Não foi possível consultar os dados.", parse_mode='HTML')

    ano_atual = datetime.now().year
    print(pilotos)
    message = f"<b>Campeonato de Pilotos - {ano_atual}</b>\n"

    ind = 1
    #piloto['position']
    for piloto in pilotos:
        nome_completo = f"{ piloto['Driver']['givenName'] } { piloto['Driver']['familyName'] }"
        message += f"{ ind } - { nome_completo } - { piloto['points'] }\n"
        ind = ind+1

    await update.message.reply_text(message, parse_mode='HTML')
