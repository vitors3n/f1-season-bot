import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from servicos import configuracoes


class ConfiguracoesTest(unittest.TestCase):
    def setUp(self):
        self.diretorio_temporario = tempfile.TemporaryDirectory()
        banco = Path(self.diretorio_temporario.name) / "configuracoes.sqlite"
        self.patch_banco = patch.object(configuracoes, "SETTINGS_DATABASE_PATH", str(banco))
        self.patch_minutos = patch.object(configuracoes, "REMINDER_MINUTES", (10, 5))
        self.patch_banco.start()
        self.patch_minutos.start()

    def tearDown(self):
        self.patch_banco.stop()
        self.patch_minutos.stop()
        self.diretorio_temporario.cleanup()

    def test_chat_novo_usa_antecedencias_padrao(self):
        configuracao = configuracoes.obter_configuracoes(123)

        self.assertEqual(configuracao["reminder_minutes"], (10, 5))

    def test_alternar_antecedencia_persiste_por_chat(self):
        configuracao = configuracoes.alternar_antecedencia(123, 30)

        self.assertEqual(configuracao["reminder_minutes"], (30, 10, 5))
        self.assertEqual(
            configuracoes.obter_configuracoes(123)["reminder_minutes"],
            (30, 10, 5),
        )
        self.assertEqual(
            configuracoes.obter_configuracoes(456)["reminder_minutes"],
            (10, 5),
        )

    def test_nao_remove_a_ultima_antecedencia(self):
        configuracoes.alternar_antecedencia(123, 10)
        configuracao = configuracoes.alternar_antecedencia(123, 5)

        self.assertEqual(configuracao["reminder_minutes"], (5,))
        configuracao = configuracoes.alternar_antecedencia(123, 5)
        self.assertEqual(configuracao["reminder_minutes"], (5,))

    def test_restaurar_padrao_restaura_antecedencias(self):
        configuracoes.alternar_antecedencia(123, 30)
        configuracao = configuracoes.restaurar_configuracoes(123)

        self.assertEqual(configuracao["reminder_minutes"], (10, 5))
