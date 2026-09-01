from comandos.mensagens import ERRO_CONSULTA, classificacao_pilotos
from servicos.campeonato_pilotos import campeonato_pilotos
from telegram.ext import ContextTypes
from datetime import datetime
from telegram import Update


async def drivers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pilotos = campeonato_pilotos()
    if pilotos is None:
        await update.message.reply_text(ERRO_CONSULTA)
        return
    ano_atual = datetime.now().year
    await update.message.reply_text(
        classificacao_pilotos(pilotos, ano_atual), parse_mode='HTML'
    )
