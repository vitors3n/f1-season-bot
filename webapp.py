"""Servidor local do dashboard do Telegram Mini App."""

import asyncio
import json
import logging
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from servicos.http_client import encerrar_http_client
from servicos.pega_corrida import pega_corrida


LOGGER = logging.getLogger(__name__)
STATIC_DIRECTORY = Path(__file__).parent / "webapp"
HOST = os.getenv("WEB_APP_HOST", "127.0.0.1")
PORT = int(os.getenv("WEB_APP_PORT", "8000"))


def montar_proxima_corrida(corrida):
    """Converte o modelo compartilhado em dados seguros para o frontend."""
    sessoes = [corrida.fp1]
    if corrida.sprint:
        sessoes.extend([corrida.sprint_quali, corrida.sprint])
    else:
        sessoes.extend([corrida.fp2, corrida.fp3])
    sessoes.extend([corrida.quali, corrida])
    return {
        "nome": corrida.nome,
        "circuito": corrida.circuito,
        "data": corrida.dia_hora(),
        "sessoes": [
            {"nome": sessao.nome, "data": sessao.dia_hora()}
            for sessao in sessoes
            if sessao is not None
        ],
    }


async def obter_proxima_corrida():
    try:
        corrida = await pega_corrida()
        return montar_proxima_corrida(corrida) if corrida else None
    finally:
        await encerrar_http_client()


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        caminho = urlparse(self.path).path
        if caminho == "/api/proxima-corrida":
            self._responder_proxima_corrida()
        elif caminho in ("/", "/index.html"):
            self._enviar_arquivo("index.html", "text/html; charset=utf-8")
        elif caminho == "/app.css":
            self._enviar_arquivo("app.css", "text/css; charset=utf-8")
        elif caminho == "/app.js":
            self._enviar_arquivo("app.js", "application/javascript; charset=utf-8")
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def _responder_proxima_corrida(self):
        try:
            corrida = asyncio.run(obter_proxima_corrida())
        except Exception:
            LOGGER.exception("Falha ao carregar a próxima corrida para o dashboard")
            self._enviar_json({"erro": "Não foi possível carregar os dados agora."}, HTTPStatus.BAD_GATEWAY)
            return
        if corrida is None:
            self._enviar_json({"erro": "Nenhuma próxima corrida foi encontrada."}, HTTPStatus.NOT_FOUND)
            return
        self._enviar_json(corrida)

    def _enviar_arquivo(self, nome, content_type):
        conteudo = (STATIC_DIRECTORY / nome).read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", len(conteudo))
        self.end_headers()
        self.wfile.write(conteudo)

    def _enviar_json(self, dados, status=HTTPStatus.OK):
        conteudo = json.dumps(dados, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(conteudo))
        self.end_headers()
        self.wfile.write(conteudo)

    def log_message(self, formato, *args):
        LOGGER.info("Dashboard: " + formato, *args)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    servidor = ThreadingHTTPServer((HOST, PORT), DashboardHandler)
    LOGGER.info("Dashboard disponível em http://%s:%s", HOST, PORT)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        LOGGER.info("Dashboard encerrado")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()
