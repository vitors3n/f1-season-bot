"""Servidor local do dashboard do Telegram Mini App."""

import asyncio
import hashlib
import hmac
import json
import logging
import os
import secrets
import sqlite3
import time
from datetime import datetime, timedelta
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qsl, urlparse

from config import BOT_TOKEN
from servicos.http_client import busca_json, encerrar_http_client
from servicos.pega_corrida import pega_corrida
from servicos.campeonato_pilotos import campeonato_pilotos


LOGGER = logging.getLogger(__name__)
STATIC_DIRECTORY = Path(__file__).parent / "webapp"
HOST = os.getenv("WEB_APP_HOST", "127.0.0.1")
PORT = int(os.getenv("WEB_APP_PORT", "8000"))
AUTH_DATABASE_PATH = os.getenv("WEB_APP_DATABASE_PATH", "data/webapp.sqlite")
SESSION_TTL_SECONDS = int(os.getenv("WEB_APP_SESSION_TTL", str(7 * 24 * 60 * 60)))
INIT_DATA_MAX_AGE_SECONDS = int(os.getenv("WEB_APP_INIT_DATA_MAX_AGE", "86400"))
COOKIE_SECURE = os.getenv("WEB_APP_COOKIE_SECURE", "1") == "1"
ADMIN_TELEGRAM_IDS = frozenset(
    int(item.strip())
    for item in os.getenv("ADMIN_TELEGRAM_IDS", "101343650").split(",")
    if item.strip()
)


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


def inicializar_banco():
    Path(AUTH_DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
    conexao = sqlite3.connect(AUTH_DATABASE_PATH)
    try:
        conexao.executescript("""
            CREATE TABLE IF NOT EXISTS webapp_users (
                telegram_id INTEGER PRIMARY KEY,
                first_name TEXT NOT NULL,
                username TEXT,
                updated_at INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS webapp_sessions (
                token TEXT PRIMARY KEY,
                telegram_id INTEGER NOT NULL,
                expires_at INTEGER NOT NULL,
                FOREIGN KEY (telegram_id) REFERENCES webapp_users (telegram_id)
            );
            CREATE TABLE IF NOT EXISTS top5_predictions (
                race_key TEXT NOT NULL,
                telegram_id INTEGER NOT NULL,
                position INTEGER NOT NULL CHECK(position BETWEEN 1 AND 5),
                driver_id TEXT NOT NULL,
                updated_at INTEGER NOT NULL,
                PRIMARY KEY (race_key, telegram_id, position),
                FOREIGN KEY (telegram_id) REFERENCES webapp_users (telegram_id)
            );
            CREATE TABLE IF NOT EXISTS top5_results (
                race_key TEXT NOT NULL,
                position INTEGER NOT NULL CHECK(position BETWEEN 1 AND 5),
                driver_id TEXT NOT NULL,
                updated_by INTEGER NOT NULL,
                updated_at INTEGER NOT NULL,
                PRIMARY KEY (race_key, position)
            );
        """)
    finally:
        conexao.close()


def validar_init_data(init_data):
    if not BOT_TOKEN:
        raise ValueError("Autenticação do Telegram não está configurada.")

    dados = dict(parse_qsl(init_data, keep_blank_values=True))
    hash_recebido = dados.pop("hash", None)
    if not hash_recebido or "user" not in dados or "auth_date" not in dados:
        raise ValueError("Dados de autenticação incompletos.")

    try:
        auth_date = int(dados["auth_date"])
    except ValueError as erro:
        raise ValueError("Data de autenticação inválida.") from erro
    if abs(int(time.time()) - auth_date) > INIT_DATA_MAX_AGE_SECONDS:
        raise ValueError("A autenticação expirou. Abra o Mini App novamente.")

    data_check_string = "\n".join(f"{chave}={dados[chave]}" for chave in sorted(dados))
    chave_secreta = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    hash_calculado = hmac.new(chave_secreta, data_check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(hash_calculado, hash_recebido):
        raise ValueError("Assinatura de autenticação inválida.")

    try:
        usuario = json.loads(dados["user"])
        telegram_id = int(usuario["id"])
        first_name = str(usuario["first_name"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as erro:
        raise ValueError("Usuário do Telegram inválido.") from erro
    return {"telegram_id": telegram_id, "first_name": first_name, "username": usuario.get("username")}


def criar_sessao(usuario):
    agora = int(time.time())
    expira_em = agora + SESSION_TTL_SECONDS
    token = secrets.token_urlsafe(32)
    conexao = sqlite3.connect(AUTH_DATABASE_PATH)
    try:
        conexao.execute(
            """INSERT INTO webapp_users (telegram_id, first_name, username, updated_at)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(telegram_id) DO UPDATE SET
                   first_name = excluded.first_name,
                   username = excluded.username,
                   updated_at = excluded.updated_at""",
            (usuario["telegram_id"], usuario["first_name"], usuario["username"], agora),
        )
        conexao.execute("DELETE FROM webapp_sessions WHERE expires_at <= ?", (agora,))
        conexao.execute(
            "INSERT INTO webapp_sessions (token, telegram_id, expires_at) VALUES (?, ?, ?)",
            (token, usuario["telegram_id"], expira_em),
        )
        conexao.commit()
    finally:
        conexao.close()
    return token


def usuario_da_sessao(cabecalho_cookie):
    if not cabecalho_cookie:
        return None
    cookies = dict(item.strip().split("=", 1) for item in cabecalho_cookie.split(";") if "=" in item)
    token = cookies.get("f1_session")
    if not token:
        return None
    conexao = sqlite3.connect(AUTH_DATABASE_PATH)
    try:
        linha = conexao.execute(
            """SELECT u.telegram_id, u.first_name, u.username
               FROM webapp_sessions s JOIN webapp_users u ON u.telegram_id = s.telegram_id
               WHERE s.token = ? AND s.expires_at > ?""",
            (token, int(time.time())),
        ).fetchone()
    finally:
        conexao.close()
    if not linha:
        return None
    return {"telegram_id": linha[0], "first_name": linha[1], "username": linha[2]}


async def obter_dados_top5():
    try:
        corrida = await pega_corrida()
        pilotos = await campeonato_pilotos()
        return corrida, pilotos
    finally:
        await encerrar_http_client()


async def obter_dados_admin():
    try:
        dados = await busca_json("https://api.jolpi.ca/ergast/f1/current/last/results.json")
        corridas = dados.get("MRData", {}).get("RaceTable", {}).get("Races", []) if dados else []
        pilotos = await campeonato_pilotos()
        return (corridas[0] if corridas else None), pilotos
    finally:
        await encerrar_http_client()


def chave_corrida(corrida):
    return f"{corrida.dia}:{corrida.nome}"


def prazo_top5(corrida):
    inicio_corrida = corrida.dia_hora_datetime()
    if inicio_corrida is None:
        return None
    return inicio_corrida - timedelta(minutes=30)


def top5_aberto(corrida):
    prazo = prazo_top5(corrida)
    return prazo is not None and datetime.now(prazo.tzinfo) < prazo


def serializar_pilotos(pilotos):
    return [
        {
            "id": piloto["Driver"]["driverId"],
            "nome": f'{piloto["Driver"]["givenName"]} {piloto["Driver"]["familyName"]}',
            "codigo": piloto["Driver"].get("code"),
        }
        for piloto in (pilotos or [])
    ]


def carregar_top5(telegram_id, corrida):
    conexao = sqlite3.connect(AUTH_DATABASE_PATH)
    try:
        linhas = conexao.execute(
            """SELECT position, driver_id FROM top5_predictions
               WHERE race_key = ? AND telegram_id = ? ORDER BY position""",
            (chave_corrida(corrida), telegram_id),
        ).fetchall()
    finally:
        conexao.close()
    return [linha[1] for linha in linhas]


def salvar_top5(telegram_id, corrida, pilotos):
    if len(pilotos) != 5 or len(set(pilotos)) != 5:
        raise ValueError("Escolha cinco pilotos diferentes.")
    if not top5_aberto(corrida):
        raise PermissionError("Os palpites fecharam 30 minutos antes da corrida.")

    agora = int(time.time())
    conexao = sqlite3.connect(AUTH_DATABASE_PATH)
    try:
        conexao.execute(
            "DELETE FROM top5_predictions WHERE race_key = ? AND telegram_id = ?",
            (chave_corrida(corrida), telegram_id),
        )
        conexao.executemany(
            """INSERT INTO top5_predictions (race_key, telegram_id, position, driver_id, updated_at)
               VALUES (?, ?, ?, ?, ?)""",
            [(chave_corrida(corrida), telegram_id, posicao, piloto, agora) for posicao, piloto in enumerate(pilotos, 1)],
        )
        conexao.commit()
    finally:
        conexao.close()


def resposta_top5(usuario, corrida, pilotos):
    prazo = prazo_top5(corrida)
    return {
        "corrida": corrida.nome,
        "fechamento": prazo.isoformat() if prazo else None,
        "aberto": top5_aberto(corrida),
        "pilotos": serializar_pilotos(pilotos),
        "previsao": carregar_top5(usuario["telegram_id"], corrida),
    }


def usuario_e_admin(usuario):
    return usuario["telegram_id"] in ADMIN_TELEGRAM_IDS


def chave_corrida_api(corrida):
    return f'{corrida["date"]}:{corrida["raceName"]}'


def carregar_resultado_top5(corrida):
    conexao = sqlite3.connect(AUTH_DATABASE_PATH)
    try:
        linhas = conexao.execute(
            "SELECT driver_id FROM top5_results WHERE race_key = ? ORDER BY position",
            (chave_corrida_api(corrida),),
        ).fetchall()
    finally:
        conexao.close()
    return [linha[0] for linha in linhas]


def salvar_resultado_top5(admin_id, corrida, pilotos):
    if len(pilotos) != 5 or len(set(pilotos)) != 5:
        raise ValueError("Escolha cinco pilotos diferentes.")
    agora = int(time.time())
    conexao = sqlite3.connect(AUTH_DATABASE_PATH)
    try:
        conexao.execute("DELETE FROM top5_results WHERE race_key = ?", (chave_corrida_api(corrida),))
        conexao.executemany(
            """INSERT INTO top5_results (race_key, position, driver_id, updated_by, updated_at)
               VALUES (?, ?, ?, ?, ?)""",
            [(chave_corrida_api(corrida), posicao, piloto, admin_id, agora) for posicao, piloto in enumerate(pilotos, 1)],
        )
        conexao.commit()
    finally:
        conexao.close()


def resposta_admin(corrida, pilotos):
    return {
        "corrida": {"nome": corrida["raceName"], "data": corrida["date"]},
        "pilotos": serializar_pilotos(pilotos),
        "resultado": carregar_resultado_top5(corrida),
    }


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        caminho = urlparse(self.path).path
        if caminho == "/api/me":
            self._responder_usuario()
        elif caminho == "/api/top5":
            self._responder_top5()
        elif caminho == "/api/admin/top5":
            self._responder_admin_top5()
        elif caminho == "/api/proxima-corrida":
            self._responder_proxima_corrida()
        elif caminho in ("/", "/index.html"):
            self._enviar_arquivo("index.html", "text/html; charset=utf-8")
        elif caminho == "/app.css":
            self._enviar_arquivo("app.css", "text/css; charset=utf-8")
        elif caminho == "/app.js":
            self._enviar_arquivo("app.js", "application/javascript; charset=utf-8")
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self):
        caminho = urlparse(self.path).path
        if caminho == "/api/top5":
            self._salvar_top5()
            return
        if caminho == "/api/admin/top5":
            self._salvar_admin_top5()
            return
        if caminho != "/api/auth/telegram":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        try:
            tamanho = int(self.headers.get("Content-Length", "0"))
            if tamanho <= 0 or tamanho > 16_384:
                raise ValueError("Requisição de autenticação inválida.")
            corpo = json.loads(self.rfile.read(tamanho))
            usuario = validar_init_data(corpo["init_data"])
            token = criar_sessao(usuario)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as erro:
            self._enviar_json({"erro": str(erro)}, HTTPStatus.UNAUTHORIZED)
            return
        self._enviar_json({"usuario": usuario}, headers={"Set-Cookie": self._cookie_sessao(token)})

    def _responder_usuario(self):
        usuario = self._usuario_autenticado()
        if usuario:
            self._enviar_json({"usuario": usuario})

    def _usuario_autenticado(self):
        usuario = usuario_da_sessao(self.headers.get("Cookie"))
        if not usuario:
            self._enviar_json({"erro": "Faça login pelo Telegram para acessar o dashboard."}, HTTPStatus.UNAUTHORIZED)
        return usuario

    def _responder_proxima_corrida(self):
        if not self._usuario_autenticado():
            return
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

    def _responder_top5(self):
        usuario = self._usuario_autenticado()
        if not usuario:
            return
        try:
            corrida, pilotos = asyncio.run(obter_dados_top5())
            if corrida is None or pilotos is None:
                raise ValueError("Não foi possível carregar os dados da corrida.")
            self._enviar_json(resposta_top5(usuario, corrida, pilotos))
        except ValueError as erro:
            self._enviar_json({"erro": str(erro)}, HTTPStatus.BAD_GATEWAY)
        except Exception:
            LOGGER.exception("Falha ao carregar a previsão Top 5")
            self._enviar_json({"erro": "Não foi possível carregar o Top 5 agora."}, HTTPStatus.BAD_GATEWAY)

    def _usuario_admin(self):
        usuario = self._usuario_autenticado()
        if usuario and not usuario_e_admin(usuario):
            self._enviar_json({"erro": "Acesso administrativo nao autorizado."}, HTTPStatus.FORBIDDEN)
            return None
        return usuario

    def _responder_admin_top5(self):
        if not self._usuario_admin():
            return
        try:
            corrida, pilotos = asyncio.run(obter_dados_admin())
            if corrida is None or pilotos is None:
                raise ValueError("Nao foi possivel carregar a ultima corrida.")
            self._enviar_json(resposta_admin(corrida, pilotos))
        except ValueError as erro:
            self._enviar_json({"erro": str(erro)}, HTTPStatus.BAD_GATEWAY)
        except Exception:
            LOGGER.exception("Falha ao carregar a area administrativa")
            self._enviar_json({"erro": "Nao foi possivel carregar a area administrativa."}, HTTPStatus.BAD_GATEWAY)

    def _salvar_top5(self):
        usuario = self._usuario_autenticado()
        if not usuario:
            return
        try:
            tamanho = int(self.headers.get("Content-Length", "0"))
            corpo = json.loads(self.rfile.read(tamanho))
            escolhidos = corpo["pilotos"]
            if not isinstance(escolhidos, list) or not all(isinstance(item, str) for item in escolhidos):
                raise ValueError("Previsão inválida.")
            corrida, pilotos = asyncio.run(obter_dados_top5())
            if corrida is None or pilotos is None:
                raise ValueError("Não foi possível carregar os dados da corrida.")
            pilotos_disponiveis = {piloto["id"] for piloto in serializar_pilotos(pilotos)}
            if not set(escolhidos).issubset(pilotos_disponiveis):
                raise ValueError("Um ou mais pilotos não são válidos.")
            salvar_top5(usuario["telegram_id"], corrida, escolhidos)
            self._enviar_json(resposta_top5(usuario, corrida, pilotos))
        except PermissionError as erro:
            self._enviar_json({"erro": str(erro)}, HTTPStatus.FORBIDDEN)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as erro:
            self._enviar_json({"erro": str(erro)}, HTTPStatus.BAD_REQUEST)
        except Exception:
            LOGGER.exception("Falha ao salvar a previsão Top 5")
            self._enviar_json({"erro": "Não foi possível salvar o Top 5 agora."}, HTTPStatus.BAD_GATEWAY)

    def _salvar_admin_top5(self):
        usuario = self._usuario_admin()
        if not usuario:
            return
        try:
            tamanho = int(self.headers.get("Content-Length", "0"))
            corpo = json.loads(self.rfile.read(tamanho))
            escolhidos = corpo["pilotos"]
            if not isinstance(escolhidos, list) or not all(isinstance(item, str) for item in escolhidos):
                raise ValueError("Resultado invalido.")
            corrida, pilotos = asyncio.run(obter_dados_admin())
            if corrida is None or pilotos is None:
                raise ValueError("Nao foi possivel carregar a ultima corrida.")
            pilotos_disponiveis = {piloto["id"] for piloto in serializar_pilotos(pilotos)}
            if not set(escolhidos).issubset(pilotos_disponiveis):
                raise ValueError("Um ou mais pilotos nao sao validos.")
            salvar_resultado_top5(usuario["telegram_id"], corrida, escolhidos)
            self._enviar_json(resposta_admin(corrida, pilotos))
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as erro:
            self._enviar_json({"erro": str(erro)}, HTTPStatus.BAD_REQUEST)
        except Exception:
            LOGGER.exception("Falha ao salvar o resultado Top 5")
            self._enviar_json({"erro": "Nao foi possivel salvar o resultado agora."}, HTTPStatus.BAD_GATEWAY)

    def _enviar_arquivo(self, nome, content_type):
        conteudo = (STATIC_DIRECTORY / nome).read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", len(conteudo))
        self.end_headers()
        self.wfile.write(conteudo)

    def _cookie_sessao(self, token):
        atributos = [f"f1_session={token}", "HttpOnly", "SameSite=Lax", "Path=/", f"Max-Age={SESSION_TTL_SECONDS}"]
        if COOKIE_SECURE:
            atributos.append("Secure")
        return "; ".join(atributos)

    def _enviar_json(self, dados, status=HTTPStatus.OK, headers=None):
        conteudo = json.dumps(dados, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(conteudo))
        for chave, valor in (headers or {}).items():
            self.send_header(chave, valor)
        self.end_headers()
        self.wfile.write(conteudo)

    def log_message(self, formato, *args):
        LOGGER.info("Dashboard: " + formato, *args)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    inicializar_banco()
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
