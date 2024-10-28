from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from models.corrida import Corrida
from dotenv import load_dotenv
from datetime import datetime
from diskcache import Cache
from telegram import Update
import requests
import logging
import pytz
import os

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

url = "https://api.jolpi.ca/ergast/f1/2024/21.json"

cache = Cache('jolpi_cache')

logger = logging.getLogger(__name__)

def dataCorrida(data_corrida):
    data_corrida_datetime = datetime.strptime(data_corrida, "%Y-%m-%d %H:%M:%SZ").replace(tzinfo=pytz.UTC)
    data_corrida_datetime = data_corrida_datetime.astimezone(pytz.timezone("America/Sao_Paulo"))
    data_hoje = datetime.now().astimezone(pytz.timezone("America/Sao_Paulo"))

    if data_corrida_datetime < data_hoje:
        return True
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello")

async def proxima(update: Update, context: ContextTypes.DEFAULT_TYPE):

    data = cache.get(url)
    
    if data is not None:
        print('Usando cache')
    else:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            cache.set(url, data, expire=10*24*60*60)

    race_table = data['MRData']['RaceTable']
    rounds = race_table['Races']

    round_numero = 0

    for round in rounds:
        if dataCorrida(f"{round['date']} {round['time']}"):
            pass
        else:
            round_numero = round
            break

    round_atual = Corrida(round_numero)

    message = (
        f"<b>{ round_atual.granprix }</b>\n"
        f"{ round_atual.circuito }\n\n"
    )   

    message+= f"<b>FP1:</b> { round_atual.fp1.dia_hora() }\n\n"
    if round_atual.fp2:
        message+= f"<b>FP2:</b> { round_atual.fp2.dia_hora() }\n\n"
    if round_atual.fp3:
        message+= f"<b>FP3:</b> { round_atual.fp3.dia_hora() }\n\n"
    if round_atual.sprint_quali:
        message+= f"<b>SprintQuali:</b> { round_atual.sprint_quali.dia_hora() }\n\n"
        message+= f"<b>Sprint:</b> { round_atual.sprint.dia_hora() }\n\n"
    message+= f"<b>Quali:</b> { round_atual.quali.dia_hora() }\n\n"

    message+= f"<b>Corrida:</b> { round_atual.dia_hora() }"

    await update.message.reply_text(message, parse_mode='HTML')

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("proxima", proxima))
    application.run_polling()

if __name__ == "__main__":
    main()