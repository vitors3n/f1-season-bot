import json
import sqlite3
from pathlib import Path

from config import DEFAULT_TIMEZONE, REMINDER_MINUTES, SETTINGS_DATABASE_PATH


SESSOES_PADRAO = ("fp1", "fp2", "fp3", "sprint_quali", "sprint", "quali", "race")


def _conexao():
    caminho = Path(SETTINGS_DATABASE_PATH)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    conexao = sqlite3.connect(caminho)
    conexao.execute(
        """
        CREATE TABLE IF NOT EXISTS configuracoes_chat (
            chat_id INTEGER PRIMARY KEY,
            timezone TEXT NOT NULL,
            language TEXT NOT NULL,
            reminder_minutes TEXT NOT NULL,
            sessions TEXT NOT NULL
        )
        """
    )
    return conexao


def configuracao_padrao():
    return {
        "timezone": DEFAULT_TIMEZONE,
        "language": "pt_BR",
        "reminder_minutes": REMINDER_MINUTES,
        "sessions": SESSOES_PADRAO,
    }


def obter_configuracoes(chat_id):
    with _conexao() as conexao:
        linha = conexao.execute(
            "SELECT timezone, language, reminder_minutes, sessions "
            "FROM configuracoes_chat WHERE chat_id = ?",
            (chat_id,),
        ).fetchone()

    if linha is None:
        return configuracao_padrao()

    return {
        "timezone": linha[0],
        "language": linha[1],
        "reminder_minutes": tuple(json.loads(linha[2])),
        "sessions": tuple(json.loads(linha[3])),
    }


def salvar_configuracoes(chat_id, configuracoes):
    with _conexao() as conexao:
        conexao.execute(
            """
            INSERT INTO configuracoes_chat
                (chat_id, timezone, language, reminder_minutes, sessions)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET
                timezone = excluded.timezone,
                language = excluded.language,
                reminder_minutes = excluded.reminder_minutes,
                sessions = excluded.sessions
            """,
            (
                chat_id,
                configuracoes["timezone"],
                configuracoes["language"],
                json.dumps(configuracoes["reminder_minutes"]),
                json.dumps(configuracoes["sessions"]),
            ),
        )


def alternar_sessao(chat_id, sessao):
    configuracoes = obter_configuracoes(chat_id)
    sessoes = set(configuracoes["sessions"])
    if sessao in sessoes and len(sessoes) > 1:
        sessoes.remove(sessao)
    else:
        sessoes.add(sessao)
    configuracoes["sessions"] = tuple(
        item for item in SESSOES_PADRAO if item in sessoes
    )
    salvar_configuracoes(chat_id, configuracoes)
    return configuracoes


def restaurar_configuracoes(chat_id):
    configuracoes = configuracao_padrao()
    salvar_configuracoes(chat_id, configuracoes)
    return configuracoes
