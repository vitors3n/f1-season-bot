from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes
from comandos.notify import (
    clear_notify,
    encerrar_scheduler,
    iniciar_scheduler,
    listnotify,
    notify,
)
from comandos.next import next
from comandos.calendar import calendar
from comandos.countdown import countdown
from comandos.about import about
from comandos.help import help_command
from comandos.qualifying import qualifying
from comandos.weather import weather
from comandos.drivers import drivers
from comandos.teams import teams
from comandos.settings import settings, settings_callback
from comandos.mensagens import MENSAGEM_INICIAL
from config import BOT_TOKEN, LOG_LEVEL
from telegram import Update
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=LOG_LEVEL
)

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(MENSAGEM_INICIAL, parse_mode='HTML')


async def iniciar_aplicacao(application):
    iniciar_scheduler()


async def encerrar_aplicacao(application):
    encerrar_scheduler()

def main():
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(iniciar_aplicacao)
        .post_stop(encerrar_aplicacao)
        .build()
    )
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("next", next))
    application.add_handler(CommandHandler("calendar", calendar))
    application.add_handler(CommandHandler("countdown", countdown))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("qualifying", qualifying))
    application.add_handler(CommandHandler("weather", weather))
    application.add_handler(CommandHandler("notify", notify))
    application.add_handler(CommandHandler("listnotify", listnotify))
    application.add_handler(CommandHandler("clearnotify", clear_notify))
    application.add_handler(CommandHandler("drivers", drivers))
    application.add_handler(CommandHandler("teams", teams))
    application.add_handler(CommandHandler("settings", settings))
    application.add_handler(CallbackQueryHandler(settings_callback, pattern="^settings:"))
    application.run_polling()

if __name__ == "__main__":
    main()
