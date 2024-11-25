FROM python:3.11-slim

RUN adduser --system --no-create-home f1bot

WORKDIR /usr/src/f1-bot
COPY requirements.txt /usr/src/f1-bot
RUN pip install --no-cache-dir -r requirements.txt

COPY comandos /usr/src/f1-bot/comandos
COPY modelos /usr/src/f1-bot/modelos
COPY utils /usr/src/f1-bot/utils
COPY bot.py /usr/src/f1-bot/

USER f1bot

CMD ["python", "bot.py"]