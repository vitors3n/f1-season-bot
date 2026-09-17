import logging

import httpx

from config import REQUEST_TIMEOUT

cliente_http = None
logger = logging.getLogger(__name__)


async def iniciar_http_client():
    global cliente_http
    if cliente_http is None or cliente_http.is_closed:
        cliente_http = httpx.AsyncClient(timeout=REQUEST_TIMEOUT)
        logger.info("Cliente HTTP iniciado")


async def encerrar_http_client():
    global cliente_http
    if cliente_http is not None:
        await cliente_http.aclose()
        cliente_http = None
        logger.info("Cliente HTTP encerrado")


async def busca_json(url, params=None):
    try:
        await iniciar_http_client()
        response = await cliente_http.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as erro:
        logger.warning("Falha na consulta HTTP para %s: %s", url, erro)
        return None
    except ValueError:
        logger.warning("Resposta JSON inválida recebida de %s", url)
        return None
