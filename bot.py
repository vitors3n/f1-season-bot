from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from models.corrida import Corrida
from dotenv import load_dotenv
from datetime import datetime
from diskcache import Cache
from telegram import Update
from telegram import Bot
import requests
import logging
import pytz
import os
import asyncio

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

url = "https://api.jolpi.ca/ergast/f1/2024/21.json"

cache = Cache('jolpi_cache')

logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)

def adicionaLembrete(scheduler, data_completa, update):
    chat_id = update.message.chat.id
    message_thread_id = update.message.message_thread_id
    
    reminder_10_minutes = data_completa - timedelta(minutes=10)
    reminder_5_minutes = data_completa - timedelta(minutes=5)

    scheduler.add_job(enviar_lembrete, 'date', run_date=reminder_10_minutes, args=[update, chat_id, message_thread_id, 10])
    scheduler.add_job(enviar_lembrete, 'date', run_date=reminder_5_minutes, args=[update, chat_id, message_thread_id, 5])
    print('Lembretes adicionados.')

async def enviar_lembrete(update, chat_id, message_thread_id, minutes_before):
    print(f"Lembrete: {minutes_before} minutos para o próximo evento começar")
    await bot.send_message(chat_id=chat_id, text=f"Lembrete: {minutes_before} minutos para o próximo evento começar", reply_to_message_id=message_thread_id)

async def notify(update: Update, context: ContextTypes.DEFAULT_TYPE):

    scheduler = AsyncIOScheduler()
    jobs = scheduler.get_jobs()

    round = pega_round()
    evento_corrida = round.dia_hora_datetime()
    evento_fp1 = round.fp1.dia_hora_datetime()
    evento_quali = round.quali.dia_hora_datetime()

    adicionaLembrete(scheduler, evento_corrida, update)
    adicionaLembrete(scheduler, evento_fp1, update)
    adicionaLembrete(scheduler, evento_quali, update)

    if round.sprint_quali:
        evento_spring_quali = round.sprint_quali.dia_hora_datetime()
        evento_spring = round.sprint.dia_hora_datetime()
        adicionaLembrete(scheduler, evento_spring_quali, update)
        adicionaLembrete(scheduler, evento_spring, update)
    
    if not round.sprint_quali:
        evento_fp2 = round.fp2.dia_hora_datetime()
        evento_fp3 = round.fp3.dia_hora_datetime()
        adicionaLembrete(scheduler, evento_fp2, update)
        adicionaLembrete(scheduler, evento_fp3, update)

    scheduler.start()
    await update.message.reply_text("Notificação foi ligada.")

    for job in jobs:
        print(f"Job ID: {job.id}, próxima run: {job.next_run_time}")

def dataCorrida(data_corrida):
    data_corrida_datetime = datetime.strptime(data_corrida, "%Y-%m-%d %H:%M:%SZ").replace(tzinfo=pytz.UTC)
    data_corrida_datetime = data_corrida_datetime.astimezone(pytz.timezone("America/Sao_Paulo"))
    data_hoje = datetime.now().astimezone(pytz.timezone("America/Sao_Paulo"))

    if data_corrida_datetime < data_hoje:
        return True
    return False

def pega_round():
    data = cache.get(url)
    
    if data is not None:
        print('~ Usando cache ~')
    else:
        response = requests.get(url)
        print('~ Usando API ~')
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

    return round_atual

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello")

async def proxima(update: Update, context: ContextTypes.DEFAULT_TYPE):
    round_atual = pega_round()

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
    application.add_handler(CommandHandler("notify", notify))
    application.run_polling()

if __name__ == "__main__":
    main()