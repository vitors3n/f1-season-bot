from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
import logging
from dotenv import load_dotenv
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
import pytz


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

url = "https://api.jolpi.ca/ergast/f1/2024/21.json"

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello")

async def proxima(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        round = data
        next_round = round['MRData']['RaceTable']
        print(next_round['Races'][0])
        nome = next_round['Races'][0]['raceName']
        circuito = next_round['Races'][0]['Circuit']['circuitName']
        dia = next_round['Races'][0]['date']
        hora = next_round['Races'][0]['time']

        utc_string = f"{dia}T{hora}"

        utc_time = datetime.strptime(utc_string, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.UTC)

        local_time = utc_time.astimezone(pytz.timezone("America/Sao_Paulo"))
        local_time = local_time.strftime("%d/%m/%Y, %H:%M")

        message = (
            f"{ nome }\n"
            f"{ circuito }\n"
            f"{ local_time }\n"
        )
    await update.message.reply_text(message)

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("proxima", proxima))
    application.run_polling()

if __name__ == "__main__":
    main()