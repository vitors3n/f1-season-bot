from utils.pega_corrida import pega_corrida
from telegram.ext import ContextTypes
from telegram import Update

async def next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    corrida = pega_corrida()

    message = f"<b>{ corrida.nome }</b>\n"
    message += f"{ corrida.circuito }\n\n"
    message += f"<b>FP1:</b> { corrida.fp1.dia_hora() }\n\n"

    if corrida.sprint:
        message += f"<b>SprintQuali:</b> { corrida.sprint_quali.dia_hora() }\n\n"
        message += f"<b>Sprint:</b> { corrida.sprint.dia_hora() }\n\n"
    if not corrida.sprint:
        message += f"<b>FP2:</b> { corrida.fp2.dia_hora() }\n\n"
        message += f"<b>FP3:</b> { corrida.fp3.dia_hora() }\n\n"

    message += f"<b>Quali:</b> { corrida.quali.dia_hora() }\n\n"
    message += f"<b>Corrida:</b> { corrida.dia_hora() }"

    await update.message.reply_text(message, parse_mode='HTML')
