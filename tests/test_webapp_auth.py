import hashlib
import hmac
import json
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
        corrida = {"date": "2026-12-01", "raceName": "GP de Teste"}
        pilotos = ["a", "b", "c", "d", "e"]

        self.assertTrue(webapp.usuario_e_admin({"telegram_id": 101343650}))
        webapp.salvar_resultado_top5(101343650, corrida, pilotos)

        self.assertEqual(webapp.carregar_resultado_top5(corrida), pilotos)


class CorridaFalsa:
    dia = "2026-12-01"
    nome = "GP de Teste"

    def __init__(self, inicio):
        self.inicio = inicio

    def dia_hora_datetime(self):
        return self.inicio
