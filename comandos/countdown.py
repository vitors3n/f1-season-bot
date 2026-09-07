from datetime import datetime

from comandos.mensagens import (
    ERRO_CONSULTA,
    contagem_regressiva,
    nenhum_evento_futuro,
)
from modelos.corrida import TIMEZONE_PADRAO
from servicos.pega_corrida import pega_corrida
from telegram import Update
from telegram.ext import ContextTypes


def _proximo_evento(corrida, agora=None):
    agora = agora or datetime.now(TIMEZONE_PADRAO)
    eventos = [corrida.fp1, corrida.quali]

    if corrida.sprint:
        eventos.extend([corrida.sprint_quali, corrida.sprint])
    else:
        eventos.extend([corrida.fp2, corrida.fp3])

    eventos.append(corrida)
    eventos_futuros = [
        evento for evento in eventos
        if evento.dia_hora_datetime() > agora
    ]

    if not eventos_futuros:
        return None

    return min(eventos_futuros, key=lambda evento: evento.dia_hora_datetime())


async def countdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    corrida = pega_corrida()
    if corrida is None:
        await update.message.reply_text(ERRO_CONSULTA)
        return

    agora = datetime.now(TIMEZONE_PADRAO)
    evento = _proximo_evento(corrida, agora)
    if evento is None:
        await update.message.reply_text(nenhum_evento_futuro(corrida.nome), parse_mode="HTML")
        return

    nome_evento = "Corrida" if evento is corrida else evento.nome
    await update.message.reply_text(
        contagem_regressiva(corrida.nome, nome_evento, evento.dia_hora_datetime(), agora),
        parse_mode="HTML",
    )
