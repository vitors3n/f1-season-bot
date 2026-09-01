from comandos.mensagens import ERRO_CONSULTA, classificacao_construtores
from servicos.campeonato_construtores import campeonato_construtores
from telegram.ext import ContextTypes
from telegram import Update
from datetime import datetime


async def teams(update: Update, context: ContextTypes.DEFAULT_TYPE):
    times = campeonato_construtores()
    if times is None:
        await update.message.reply_text(ERRO_CONSULTA)
        return
    ano_atual = datetime.now().year
    await update.message.reply_text(
        classificacao_construtores(times, ano_atual), parse_mode='HTML'
    )
