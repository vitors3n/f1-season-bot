import os
import unittest
from unittest.mock import AsyncMock, patch

os.environ["BOT_TOKEN"] = os.getenv("BOT_TOKEN") or "123456:TESTE"

from servicos import pega_corrida


class PegaCorridaTest(unittest.IsolatedAsyncioTestCase):
    async def test_retorna_none_quando_nao_ha_proxima_corrida(self):
        resposta = {"MRData": {"RaceTable": {"Races": []}}}

        with (
            patch.object(pega_corrida, "buscar_com_cache", new=AsyncMock(return_value=resposta)),
            self.assertLogs(pega_corrida.logger, "WARNING") as logs,
        ):
            corrida = await pega_corrida.pega_corrida()

        self.assertIsNone(corrida)
        self.assertIn("Resposta inválida", logs.output[0])

    async def test_retorna_none_quando_a_resposta_esta_malformada(self):
        resposta = {"MRData": {"RaceTable": {"Races": [{"raceName": "GP de Teste"}]}}}

        with patch.object(pega_corrida, "buscar_com_cache", new=AsyncMock(return_value=resposta)):
            corrida = await pega_corrida.pega_corrida()

        self.assertIsNone(corrida)
