from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from utils.pega_corrida import pega_corrida
from telegram.ext import ContextTypes
from datetime import timedelta
from dotenv import load_dotenv
from telegram import Update
from telegram import Bot
import os

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)

lembretes = {
    'default': SQLAlchemyJobStore(url='sqlite:///data/lembretes.sqlite')
}

scheduler = AsyncIOScheduler(jobstores=lembretes)
scheduler.start()

async def enviar_lembrete(chat_id, thread_id, evento_nome, minutos):
    await bot.send_message(chat_id=chat_id, text=f"{evento_nome} começa em {minutos} minuto!", reply_to_message_id=thread_id)

def adiciona_lembrete(chat_id, thread_id, evento):
    lembrete_10_minutos = evento.dia_hora_datetime() - timedelta(minutes=10)
    lembrete_5_minutos = evento.dia_hora_datetime() - timedelta(minutes=5)

    scheduler.add_job(
        enviar_lembrete,
        'date',
        run_date=lembrete_10_minutos,
        args=[chat_id, thread_id, evento.nome, 10 ],
        id=f'{evento.nome}_{evento.dia_hora()}_10min{chat_id}',
        misfire_grace_time=20
    )

    scheduler.add_job(
        enviar_lembrete,
        'date',
        run_date=lembrete_5_minutos,
        args=[chat_id, thread_id, evento.nome, 5],
        id=f'{evento.nome}_{evento.dia_hora()}_5min{chat_id}',
        misfire_grace_time=20
    )

async def notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jobs = scheduler.get_jobs()

    chat_id = update.message.chat.id
    thread_id = update.message.message_thread_id

    corrida = pega_corrida()
    lista_eventos = [corrida, corrida.fp1, corrida.quali]

    if corrida.sprint:
        lista_eventos.append(corrida.sprint_quali)
        lista_eventos.append(corrida.sprint)
    
    if not corrida.sprint:
        lista_eventos.append(corrida.fp2)
        lista_eventos.append(corrida.fp3)

    for evento in lista_eventos:
        try:
            adiciona_lembrete(chat_id, thread_id, evento)
        except ConflictingIdError:
            print('Job já existe... Ignorando...')
    await update.message.reply_text("Notificação foi ligada.")

    for job in jobs:
        print(f"Job ID: {job.id}, próxima run: {job.next_run_time}")

async def clear_notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    scheduler.remove_all_jobs()
    print("Todos os jobs foram apagados, jobs: ", scheduler.get_jobs())
    await update.message.reply_text("As notificações foram apagadas")
