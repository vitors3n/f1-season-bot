from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from models.corrida import Corrida
from dotenv import load_dotenv
from diskcache import Cache
from telegram import Update
from telegram import Bot
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
bot = Bot(token=BOT_TOKEN)

def adiciona_lembrete(scheduler, data_evento, update):
    chat_id = update.message.chat.id
    msg_thread_id = update.message.message_thread_id
    lembrete_10_minutos = data_evento - timedelta(minutes=10)
    lembrete_5_minutos = data_evento - timedelta(minutes=5)
    scheduler.add_job(enviar_lembrete, 'date', run_date=lembrete_10_minutos, args=[update, chat_id, msg_thread_id, 10])
    scheduler.add_job(enviar_lembrete, 'date', run_date=lembrete_5_minutos, args=[update, chat_id, msg_thread_id, 5])

async def enviar_lembrete(update, chat_id, message_thread_id, minutes_before):
    print(f"Lembrete: {minutes_before} minutos para o próximo evento começar")
    await bot.send_message(chat_id=chat_id, text=f"Lembrete: {minutes_before} minutos para o próximo evento começar", reply_to_message_id=message_thread_id)

async def notify(update: Update, context: ContextTypes.DEFAULT_TYPE):

    scheduler = AsyncIOScheduler()
    jobs = scheduler.get_jobs()

    corrida = pega_corrida()
    lista_eventos = [corrida, corrida.fp1, corrida.quali]

    if corrida.sprint:
        lista_eventos.append(corrida.sprint_quali)
        lista_eventos.append(corrida.sprint)
    
    if not corrida.sprint:
        lista_eventos.append(corrida.fp2)
        lista_eventos.append(corrida.fp3)

    for evento in lista_eventos:
        adiciona_lembrete(scheduler, evento.dia_hora_datetime(), update)

    scheduler.start()
    await update.message.reply_text("Notificação foi ligada.")

    for job in jobs:
        print(f"Job ID: {job.id}, próxima run: {job.next_run_time}")

def corrida_passou(data_corrida):
    data_corrida_datetime = datetime.strptime(data_corrida, "%Y-%m-%d %H:%M:%SZ").replace(tzinfo=pytz.UTC)
    data_corrida_datetime = data_corrida_datetime.astimezone(pytz.timezone("America/Sao_Paulo"))
    data_hoje = datetime.now().astimezone(pytz.timezone("America/Sao_Paulo"))

    if data_corrida_datetime < data_hoje:
        return True
    return False

def pega_corrida():
    data = cache.get(url)
    
    if data is not None:
        print('~ Usando cache ~')
    else:
        response = requests.get(url)
        print('~ Usando API ~')
        if response.status_code == 200:
            data = response.json()
            cache.set(url, data, expire=10*24*60*60)

    corridas = data['MRData']['RaceTable']['Races']

    proxima_corrida_json = ''

    for corrida in corridas:
        if corrida_passou(f"{corrida['date']} {corrida['time']}"):
            pass
        else:
            proxima_corrida_json = corrida
            break

    proxima_corrida = Corrida(proxima_corrida_json)
    return proxima_corrida

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello")

async def next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    corrida = pega_corrida()

    message = f"<b>{ corrida.granprix }</b>\n"
    message += f"{ corrida.circuito }\n\n"
    message += f"<b>FP1:</b> { corrida.fp1.dia_hora() }\n\n"

    if corrida.sprint:
        message += f"<b>SprintQuali:</b> { corrida.sprint_quali.dia_hora() }\n\n"
        message += f"<b>Sprint:</b> { corrida.sprint.dia_hora() }\n\n"
    if not corrida.sprint:
        message += f"<b>FP2:</b> { corrida.fp2.dia_hora() }\n\n"
        message += f"<b>FP3:</b> { corrida.fp3.dia_hora() }\n\n"

    message += f"<b>Quali:</b> { corrida.quali.dia_hora() }\n\n"
    message += f"<b>Corrida:</b> { corrida.dia_hora() }"

    await update.message.reply_text(message, parse_mode='HTML')

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("next", next))
    application.add_handler(CommandHandler("notify", notify))
    application.run_polling()

if __name__ == "__main__":
    main()