import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from diskcache import Cache

from servicos import calendario, http_client


def resposta_calendario():
    return {
        "MRData": {
            "RaceTable": {
                "Races": [{"season": "2026", "round": "1", "raceName": "GP de Teste"}]
            }
        }
    }


class HttpClientTest(unittest.IsolatedAsyncioTestCase):
    async def test_cliente_http_e_reutilizado_e_encerrado(self):
        cliente = SimpleNamespace(
            is_closed=False,
            get=AsyncMock(),
            aclose=AsyncMock(),
        )
        fabrica = MagicMock(return_value=cliente)

        with (
            patch.object(http_client, "cliente_http", None),
            patch.object(http_client.httpx, "AsyncClient", fabrica),
        ):
            await http_client.iniciar_http_client()
            primeiro_cliente = http_client.cliente_http
            await http_client.iniciar_http_client()
            await http_client.encerrar_http_client()
            self.assertIsNone(http_client.cliente_http)

        self.assertIs(primeiro_cliente, cliente)
        fabrica.assert_called_once_with(timeout=http_client.REQUEST_TIMEOUT)
        cliente.aclose.assert_awaited_once()

    async def test_json_invalido_retorna_none(self):
        resposta = SimpleNamespace(
            raise_for_status=MagicMock(),
            json=MagicMock(side_effect=ValueError()),
        )
        cliente = SimpleNamespace(get=AsyncMock(return_value=resposta))

        with (
            patch.object(http_client, "iniciar_http_client", new=AsyncMock()),
            patch.object(http_client, "cliente_http", cliente),
        ):
            dados = await http_client.busca_json("https://api.exemplo.test/dados")

        self.assertIsNone(dados)


class CacheTest(unittest.IsolatedAsyncioTestCase):
    async def test_calendario_reutiliza_resposta_do_cache(self):
        with tempfile.TemporaryDirectory() as diretorio:
            cache = Cache(diretorio)
            try:
                with (
                    patch.object(calendario, "cache", cache),
                    patch.object(
                        calendario,
                        "busca_json",
                        new=AsyncMock(return_value=resposta_calendario()),
                    ) as busca_json,
                ):
                    primeira_resposta = await calendario.pega_calendario()
                    segunda_resposta = await calendario.pega_calendario()
            finally:
                cache.close()

        self.assertEqual(primeira_resposta, segunda_resposta)
        busca_json.assert_awaited_once()

    async def test_falha_da_api_nao_e_armazenada_no_cache(self):
        url = "https://api.jolpi.ca/ergast/f1/current.json"
        with tempfile.TemporaryDirectory() as diretorio:
            cache = Cache(diretorio)
            try:
                with (
                    patch.object(calendario, "cache", cache),
                    patch.object(calendario, "busca_json", new=AsyncMock(return_value=None)),
                ):
                    resultado = await calendario.pega_calendario()
                    valor_cache = cache.get(url)
            finally:
                cache.close()

        self.assertIsNone(resultado)
        self.assertIsNone(valor_cache)
