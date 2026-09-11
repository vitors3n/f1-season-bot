import httpx

from config import REQUEST_TIMEOUT

cliente_http = None


async def iniciar_http_client():
    global cliente_http
    if cliente_http is None or cliente_http.is_closed:
        cliente_http = httpx.AsyncClient(timeout=REQUEST_TIMEOUT)


async def encerrar_http_client():
    global cliente_http
    if cliente_http is not None:
        await cliente_http.aclose()
        cliente_http = None


async def busca_json(url, params=None):
    try:
        await iniciar_http_client()
        response = await cliente_http.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except (httpx.HTTPError, ValueError):
        return None
