from datetime import datetime

from comandos.mensagens import (
    ERRO_CONSULTA,
    HORARIOS_INDEFINIDOS,
    PREVISAO_INDISPONIVEL,
    previsao_tempo,
)
from modelos.corrida import TIMEZONE_PADRAO
from servicos.meteorologia import pega_previsao, previsao_no_horario
from servicos.pega_corrida import pega_corrida
from telegram import Update
from telegram.ext import ContextTypes


def _eventos_da_corrida(corrida):
    eventos = [corrida.fp1]
    if corrida.sprint:
        eventos.extend([corrida.sprint_quali, corrida.sprint])
    else:
        eventos.extend([corrida.fp2, corrida.fp3])
    eventos.extend([corrida.quali, corrida])
    eventos_com_horario = [evento for evento in eventos if evento.tem_horario]
    return sorted(eventos_com_horario, key=lambda evento: evento.dia_hora_datetime())


async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    corrida = await pega_corrida()
    if corrida is None:
        await update.message.reply_text(ERRO_CONSULTA)
        return

    eventos = _eventos_da_corrida(corrida)
    if not eventos:
        await update.message.reply_text(HORARIOS_INDEFINIDOS)
        return

    previsao = await pega_previsao(corrida.latitude, corrida.longitude)
    if previsao is None:
        await update.message.reply_text(ERRO_CONSULTA)
        return

    sessoes = []
    agora = datetime.now(TIMEZONE_PADRAO)
    for evento in eventos:
        if evento.dia_hora_datetime() < agora:
            continue
        dados = previsao_no_horario(previsao, evento.dia_hora_datetime())
        if dados is not None:
            dados["nome"] = "Corrida" if evento is corrida else evento.nome
            dados["dia_hora"] = evento.dia_hora_datetime()
            sessoes.append(dados)

    if not sessoes:
        await update.message.reply_text(PREVISAO_INDISPONIVEL)
        return

    await update.message.reply_text(
        previsao_tempo(corrida.nome, corrida.circuito, sessoes),
        parse_mode="HTML",
    )
