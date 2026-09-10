from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from servicos.pega_corrida import pega_corrida
from comandos.mensagens import (
    ERRO_CONSULTA,
    HORARIOS_INDEFINIDOS,
    NOTIFICACOES_REMOVIDAS,
    lembrete,
    lista_notificacoes,
    notificacoes_ativadas,
)
from telegram.ext import ContextTypes
from datetime import timedelta
from telegram import Update
from telegram import Bot
from config import BOT_TOKEN, DATABASE_URL, REMINDER_MINUTES
from modelos.corrida import TIMEZONE_PADRAO
from servicos.configuracoes import obter_configuracoes
from servicos.permissoes import exigir_administrador

bot = Bot(token=BOT_TOKEN)

lembretes = {
    'default': SQLAlchemyJobStore(url=DATABASE_URL)
}

scheduler = AsyncIOScheduler(jobstores=lembretes, timezone=TIMEZONE_PADRAO)


def iniciar_scheduler():
    if not scheduler.running:
        scheduler.start()


def encerrar_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)

async def enviar_lembrete(chat_id, thread_id, evento_nome, minutos):
    await bot.send_message(
        chat_id=chat_id,
        text=lembrete(evento_nome, minutos),
        parse_mode='HTML',
        reply_to_message_id=thread_id,
    )

def adiciona_lembrete(chat_id, thread_id, evento, minutos_lembrete=REMINDER_MINUTES):
    dia_hora = evento.dia_hora_datetime()
    if dia_hora is None:
        return

    for minutos in minutos_lembrete:
        scheduler.add_job(
            enviar_lembrete,
            'date',
            run_date=dia_hora - timedelta(minutes=minutos),
            args=[chat_id, thread_id, evento.nome, minutos],
            id=f'{evento.nome}_{evento.dia_hora()}_{minutos}min{chat_id}',
            misfire_grace_time=20,
        )

async def notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jobs = scheduler.get_jobs()

    chat_id = update.message.chat.id
    thread_id = update.message.message_thread_id

    corrida = await pega_corrida()
    if corrida is None:
        await update.message.reply_text(ERRO_CONSULTA)
        return

    eventos_por_tipo = [("race", corrida), ("fp1", corrida.fp1), ("quali", corrida.quali)]

    if corrida.sprint:
        eventos_por_tipo.extend([("sprint_quali", corrida.sprint_quali), ("sprint", corrida.sprint)])
    
    if not corrida.sprint:
        eventos_por_tipo.extend([("fp2", corrida.fp2), ("fp3", corrida.fp3)])

    configuracoes = obter_configuracoes(chat_id)
    lista_eventos = [
        evento for tipo, evento in eventos_por_tipo
        if tipo in configuracoes["sessions"] and evento.tem_horario
    ]
    if not lista_eventos:
        await update.message.reply_text(HORARIOS_INDEFINIDOS)
        return

    for evento in lista_eventos:
        try:
            adiciona_lembrete(chat_id, thread_id, evento, configuracoes["reminder_minutes"])
        except ConflictingIdError:
            print('Job já existe... Ignorando...')
    await update.message.reply_text(
        notificacoes_ativadas(corrida.nome),
        parse_mode='HTML',
    )

    for job in jobs:
        print(f"Job ID: {job.id}, próxima run: {job.next_run_time}")

async def clear_notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await exigir_administrador(update, context):
        return

    chat_id = update.effective_chat.id

    for job in scheduler.get_jobs():
        if job.args and job.args[0] == chat_id:
            job.remove()

    await update.message.reply_text(NOTIFICACOES_REMOVIDAS)

async def listnotify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    jobs = scheduler.get_jobs()
    notificacoes = []

    for job in jobs:
        if str(chat_id) in job.id:
            readable_job_id = job.id.replace("_"," ")
            readable_job_id = readable_job_id.replace(str(chat_id), "")
            notificacoes.append(readable_job_id.strip())

    await update.message.reply_text(
        lista_notificacoes(notificacoes),
        parse_mode='HTML',
    )
