from html import escape

from servicos.ranking import lista_ranking
from telegram import Update
from telegram.ext import ContextTypes


async def ranking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    colocados = lista_ranking()
    if not colocados:
        await update.message.reply_text("🏆 Ainda não há pontuação no ranking geral.")
        return

    linhas = ["🏆 <b>Ranking geral</b>", ""]
    for colocado in colocados:
        nome = escape(colocado["nome"])
        usuario = f' (@{escape(colocado["username"])})' if colocado["username"] else ""
        linhas.append(
            f'{colocado["posicao"]}. <b>{nome}</b>{usuario} — {colocado["pontos"]} pts'
        )
    await update.message.reply_text("\n".join(linhas), parse_mode="HTML")
