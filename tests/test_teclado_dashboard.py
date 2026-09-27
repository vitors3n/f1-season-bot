import unittest

from comandos import dashboard


class TecladoDashboardTest(unittest.TestCase):
    def setUp(self):
        self.url_original = dashboard.WEB_APP_URL
        dashboard.WEB_APP_URL = "https://exemplo.test/f1/"

    def tearDown(self):
        dashboard.WEB_APP_URL = self.url_original

    def test_teclado_privado_tem_dashboard_proximo_gp_e_countdown(self):
        teclado = dashboard.teclado_dashboard("private")

        self.assertEqual(teclado.keyboard[0][0].web_app.url, "https://exemplo.test/f1/")
        self.assertEqual(teclado.keyboard[1][0].text, dashboard.BOTAO_PROXIMO_GP)
        self.assertEqual(teclado.keyboard[1][1].text, dashboard.BOTAO_COUNTDOWN)
