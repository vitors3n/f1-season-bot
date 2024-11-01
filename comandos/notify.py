from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from telegram.ext import ContextTypes
from datetime import timedelta
from utils.pega_corrida import pega_corrida
from telegram import Update

lembretes = {
    'default': SQLAlchemyJobStore(url='sqlite:///lembretes.sqlite')
}

scheduler = AsyncIOScheduler(jobstores=lembretes)
print('Iniciando Scheduler...')
scheduler.start()

async def enviar_lembrete(update, chat_id, message_thread_id, minutes_before):
    print(f"Lembrete: {minutes_before} minutos para o próximo evento começar")
    await bot.send_message(chat_id=chat_id, text=f"Lembrete: {minutes_before} minutos para o próximo evento começar", reply_to_message_id=message_thread_id)

def adiciona_lembrete(evento, update):
    chat_id = update.message.chat.id
    msg_thread_id = update.message.message_thread_id
    lembrete_10_minutos = evento.dia_hora_datetime() - timedelta(minutes=10)
    lembrete_5_minutos = evento.dia_hora_datetime() - timedelta(minutes=5)

    scheduler.add_job(
        enviar_lembrete,
        'date',
        run_date=lembrete_10_minutos,
        args=[update, chat_id, msg_thread_id, 10 ],
        id=f'{evento.nome}_{evento.dia_hora()}_10min'
    )

    scheduler.add_job(
        enviar_lembrete,
        'date',
        run_date=lembrete_5_minutos,
        args=[update, chat_id, msg_thread_id, 5],
        id=f'{evento.nome}_{evento.dia_hora()}_5min'
    )


async def notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        try:
            adiciona_lembrete(evento, update)
        except ConflictingIdError:
            print('Job já existe... Ignorando...')
    await update.message.reply_text("Notificação foi ligada.")

    for job in jobs:
        print(f"Job ID: {job.id}, próxima run: {job.next_run_time}")

async def clear_notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    scheduler.remove_all_jobs()
    print("Todos os jobs foram apagados, jobs: ", scheduler.get_jobs())
    await update.message.reply_text("As notificações foram apagadas")