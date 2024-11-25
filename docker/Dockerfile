FROM python:3.11-slim

RUN adduser --system --no-create-home f1bot

WORKDIR /usr/src/f1-bot
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./comandos /comandos
COPY ./modelos /modelos
COPY ./utils /utils
COPY ./bot.py /

USER f1bot

CMD ["python", "bot.py"]