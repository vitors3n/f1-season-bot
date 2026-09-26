import hashlib
import hmac
import json
import sqlite3
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode

import webapp


class WebAppAuthTest(unittest.TestCase):
    def setUp(self):
        self.diretorio_temporario = tempfile.TemporaryDirectory()
        webapp.AUTH_DATABASE_PATH = str(Path(self.diretorio_temporario.name) / "webapp.sqlite")
        webapp.BOT_TOKEN = "token-de-teste"
        webapp.INIT_DATA_MAX_AGE_SECONDS = 86400
        webapp.inicializar_banco()

    def tearDown(self):
        self.diretorio_temporario.cleanup()

    def _init_data_assinado(self):
        dados = {
            "auth_date": str(int(time.time())),
            "query_id": "teste",
            "user": json.dumps({"id": 123, "first_name": "Vitor", "username": "vitor"}),
        }
        data_check_string = "\n".join(f"{chave}={dados[chave]}" for chave in sorted(dados))
        chave_secreta = hmac.new(b"WebAppData", webapp.BOT_TOKEN.encode(), hashlib.sha256).digest()
        dados["hash"] = hmac.new(chave_secreta, data_check_string.encode(), hashlib.sha256).hexdigest()
        return urlencode(dados)

    def test_valida_init_data_e_cria_sessao(self):
        usuario = webapp.validar_init_data(self._init_data_assinado())
        token = webapp.criar_sessao(usuario)

        self.assertEqual(usuario["telegram_id"], 123)
        self.assertEqual(webapp.usuario_da_sessao(f"f1_session={token}")["first_name"], "Vitor")

    def test_rejeita_assinatura_invalida(self):
        init_data = self._init_data_assinado().replace("hash=", "hash=invalido")

        with self.assertRaises(ValueError):
            webapp.validar_init_data(init_data)

    def test_salva_top5_enquanto_previsoes_estao_abertas(self):
        corrida = CorridaFalsa(datetime.now(timezone.utc) + timedelta(hours=2))
        pilotos = ["max_verstappen", "lando_norris", "charles_leclerc", "george_russell", "lewis_hamilton"]

        webapp.salvar_top5(123, corrida, pilotos)

        self.assertEqual(webapp.carregar_top5(123, corrida), pilotos)

    def test_bloqueia_top5_apos_o_prazo(self):
        corrida = CorridaFalsa(datetime.now(timezone.utc) + timedelta(minutes=29))

        with self.assertRaises(PermissionError):
            webapp.salvar_top5(123, corrida, ["a", "b", "c", "d", "e"])

    def test_admin_padrao_pode_salvar_resultado_top5(self):
        corrida = {"date": "2026-12-01", "time": "15:00:00Z", "raceName": "GP de Teste"}
        pilotos = ["a", "b", "c", "d", "e"]

        self.assertTrue(webapp.usuario_e_admin({"telegram_id": 101343650}))
        webapp.salvar_resultado_top5(101343650, corrida, pilotos, datetime(2026, 12, 1, 16, tzinfo=timezone.utc))

        self.assertEqual(webapp.carregar_resultado_top5(corrida), pilotos)

    def test_calcula_pontos_por_posicao_e_top5(self):
        corrida_previsao = CorridaFalsa(datetime.now(timezone.utc) + timedelta(hours=2))
        corrida_resultado = {"date": corrida_previsao.dia, "time": "15:00:00Z", "raceName": corrida_previsao.nome}
        previsao = ["a", "b", "c", "d", "e"]
        resultado = ["a", "c", "b", "x", "e"]

        webapp.salvar_top5(123, corrida_previsao, previsao)
        webapp.salvar_resultado_top5(101343650, corrida_resultado, resultado, datetime(2026, 12, 1, 16, tzinfo=timezone.utc))

        self.assertEqual(webapp.pontuacao_usuario(123), 50)
        historico = webapp.historico_top5(123)
        self.assertEqual(historico[0]["previsao"], previsao)
        self.assertEqual(historico[0]["pontos"], 50)

    def test_janela_administrativa_abre_e_fecha_no_prazo(self):
        corrida = {"date": "2026-12-01", "time": "15:00:00Z", "raceName": "GP de Teste"}

        self.assertFalse(webapp.janela_resultado_aberta(corrida, datetime(2026, 12, 1, 15, 29, tzinfo=timezone.utc)))
        self.assertTrue(webapp.janela_resultado_aberta(corrida, datetime(2026, 12, 1, 15, 30, tzinfo=timezone.utc)))
        self.assertTrue(webapp.janela_resultado_aberta(corrida, datetime(2026, 12, 4, 15, tzinfo=timezone.utc)))
        self.assertFalse(webapp.janela_resultado_aberta(corrida, datetime(2026, 12, 4, 15, 1, tzinfo=timezone.utc)))

        with self.assertRaises(PermissionError):
            webapp.salvar_resultado_top5(
                101343650,
                corrida,
                ["a", "b", "c", "d", "e"],
                datetime(2026, 12, 1, 15, 29, tzinfo=timezone.utc),
            )

    def test_ranking_destaca_posicao_do_usuario(self):
        webapp.criar_sessao({"telegram_id": 1, "first_name": "Ana", "username": "ana"})
        webapp.criar_sessao({"telegram_id": 2, "first_name": "Bia", "username": "bia"})
        conexao = sqlite3.connect(webapp.AUTH_DATABASE_PATH)
        try:
            conexao.executemany(
                "INSERT INTO top5_scores (race_key, telegram_id, points, updated_at) VALUES (?, ?, ?, ?)",
                [("2026-01-01:GP A", 1, 50, 1), ("2026-01-01:GP A", 2, 20, 1)],
            )
            conexao.commit()
        finally:
            conexao.close()

        ranking = webapp.ranking_geral(2)

        self.assertEqual(ranking["ranking"][0]["nome"], "Ana")
        self.assertEqual(ranking["usuario"]["posicao"], 2)


class CorridaFalsa:
    dia = "2026-12-01"
    nome = "GP de Teste"

    def __init__(self, inicio):
        self.inicio = inicio

    def dia_hora_datetime(self):
        return self.inicio
