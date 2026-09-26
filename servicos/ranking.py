import sqlite3
from pathlib import Path

from config import WEB_APP_DATABASE_PATH


def lista_ranking(limite=10):
    """Retorna os líderes do bolão, com posição compartilhada em empates."""
    if not Path(WEB_APP_DATABASE_PATH).exists():
        return []

    try:
        conexao = sqlite3.connect(WEB_APP_DATABASE_PATH)
        try:
            linhas = conexao.execute(
                """SELECT u.telegram_id, u.first_name, u.username, COALESCE(SUM(s.points), 0) AS pontos
                   FROM webapp_users u
                   LEFT JOIN top5_scores s ON s.telegram_id = u.telegram_id
                   GROUP BY u.telegram_id, u.first_name, u.username
                   ORDER BY pontos DESC, u.first_name COLLATE NOCASE, u.telegram_id"""
            ).fetchall()
        finally:
            conexao.close()
    except sqlite3.Error:
        return []

    ranking = []
    pontos_anteriores = None
    posicao_atual = 0
    for indice, (_, nome, username, pontos) in enumerate(linhas, 1):
        if pontos != pontos_anteriores:
            posicao_atual = indice
            pontos_anteriores = pontos
        ranking.append({
            "posicao": posicao_atual,
            "nome": nome,
            "username": username,
            "pontos": pontos,
        })
        if len(ranking) == limite:
            break
    return ranking
