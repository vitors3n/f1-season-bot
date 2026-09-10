from comandos.mensagens import ERRO_CONSULTA, calendario_temporada
from servicos.calendario import pega_calendario
from math import ceil

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


CORRIDAS_POR_PAGINA = 5


def _pagina_corridas(corridas, pagina):
    total_paginas = ceil(len(corridas) / CORRIDAS_POR_PAGINA)
    pagina = min(max(pagina, 1), total_paginas)
    inicio = (pagina - 1) * CORRIDAS_POR_PAGINA
    return corridas[inicio:inicio + CORRIDAS_POR_PAGINA], pagina, total_paginas


def _teclado(pagina, total_paginas, usuario_id):
    botoes = []
    if pagina > 1:
        botoes.append(InlineKeyboardButton("‹ Anterior", callback_data=f"calendar:{pagina - 1}:{usuario_id}"))
    if pagina < total_paginas:
        botoes.append(InlineKeyboardButton("Próxima ›", callback_data=f"calendar:{pagina + 1}:{usuario_id}"))
    return InlineKeyboardMarkup([botoes]) if botoes else None


def _mensagem_pagina(corridas, pagina, usuario_id):
    corridas_pagina, pagina, total_paginas = _pagina_corridas(corridas, pagina)
    ano = corridas[0]["season"]
    return (
        calendario_temporada(corridas_pagina, ano, pagina, total_paginas),
        _teclado(pagina, total_paginas, usuario_id),
    )


async def calendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    corridas = await pega_calendario()
    if not corridas:
        await update.message.reply_text(ERRO_CONSULTA)
        return

    texto, teclado = _mensagem_pagina(corridas, 1, update.effective_user.id)
    await update.message.reply_text(
        texto,
        parse_mode="HTML",
        reply_markup=teclado,
    )


async def calendar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    _, pagina, usuario_id = query.data.split(":")

    if query.from_user.id != int(usuario_id):
        await query.answer("Somente quem abriu o calendário pode trocar de página.", show_alert=True)
        return

    corridas = await pega_calendario()
    if not corridas:
        await query.answer(ERRO_CONSULTA, show_alert=True)
        return

    await query.answer()
    texto, teclado = _mensagem_pagina(corridas, int(pagina), int(usuario_id))
    await query.edit_message_text(texto, parse_mode="HTML", reply_markup=teclado)
