from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
import logging
from dotenv import load_dotenv
import requests
from datetime import datetime
import pytz

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

url = "https://api.jolpi.ca/ergast/f1/2024/21.json"

logger = logging.getLogger(__name__)

def stringParaLocalTime(time_string):
        utc_time = datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.UTC)
        local_time = utc_time.astimezone(pytz.timezone("America/Sao_Paulo"))
        local_time = local_time.strftime("%d/%m/%Y, %H:%M")
        return local_time

def retornaDataString(evento):
        time_string = f"{evento['date']}T{evento['time']}"
        utc_time = datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.UTC)
        local_time = utc_time.astimezone(pytz.timezone("America/Sao_Paulo"))
        local_time = local_time.strftime("%d/%m/%Y, %H:%M")
        return local_time

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

        fp1 = next_round['Races'][0]['FirstPractice']
        fp2 = 0
        fp3 = 0
        sprint_quali = 0
        sprint = 0

        if "SecondPractice" in next_round['Races'][0]:
            fp2 = next_round['Races'][0]['SecondPractice']
        if "ThirdPractice" in next_round['Races'][0]:
            fp3 = next_round['Races'][0]['ThirdPractice']
        if "SprintQualifying" in next_round['Races'][0]:
            sprint_quali = next_round['Races'][0]['SprintQualifying']
            sprint = next_round['Races'][0]['Sprint']
        quali = next_round['Races'][0]['Qualifying']
        
        fp1_data = f"{fp1['date']}T{fp1['time']}"
        quali_data = f"{quali['date']}T{quali['time']}"

        fp1_data = stringParaLocalTime(fp1_data)
        quali_data = stringParaLocalTime(quali_data)

        utc_string = f"{dia}T{hora}"

        local_time = stringParaLocalTime(utc_string)

        message = (
            f"<b>{ nome }</b>\n"
            f"{ circuito }\n\n"
        )   

        message+= f"<b>FP1:</b> { fp1_data }\n\n"
        if fp2:
            message+= f"<b>FP2:</b> {retornaDataString(fp2)}\n\n"
        if fp3:
            message+= f"<b>FP3:</b> {retornaDataString(fp3)}\n\n"
        if sprint:
            message+= f"<b>SprintQuali:</b> {retornaDataString(sprint_quali)}\n\n"
            message+= f"<b>Sprint:</b> {retornaDataString(sprint)}\n\n"
        message+= f"<b>Quali:</b> { quali_data }\n\n"

        message+= f"<b>Corrida:</b> { local_time }"

    await update.message.reply_text(message, parse_mode='HTML')

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("proxima", proxima))
    application.run_polling()

if __name__ == "__main__":
    main()