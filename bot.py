from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from comandos.notify import clear_notify
from comandos.notify import notify
from comandos.next import next
from dotenv import load_dotenv
from telegram import Update
import logging
import os

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello")

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("next", next))
    application.add_handler(CommandHandler("notify", notify))
    application.add_handler(CommandHandler("clearnotify", clear_notify))
    application.run_polling()

if __name__ == "__main__":
    main()
