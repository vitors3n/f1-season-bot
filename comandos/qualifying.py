from comandos.mensagens import ERRO_CONSULTA, resultado_classificacao
from servicos.classificacao import pega_ultima_classificacao
from telegram import Update
from telegram.ext import ContextTypes


async def qualifying(update: Update, context: ContextTypes.DEFAULT_TYPE):
    corrida = pega_ultima_classificacao()
    if corrida is None:
        await update.message.reply_text(ERRO_CONSULTA)
        return

    await update.message.reply_text(
        resultado_classificacao(corrida),
        parse_mode="HTML",
    )
