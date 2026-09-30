import logging

from diskcache import Cache
from config import CACHE_DIRECTORY, CACHE_TTL_QUALIFYING
from servicos.cache_fallback import buscar_com_cache
from servicos.http_client import busca_json


cache = Cache(CACHE_DIRECTORY)
logger = logging.getLogger(__name__)


async def pega_ultima_classificacao():
    url = "https://api.jolpi.ca/ergast/f1/current/last/qualifying.json"
    data = await buscar_com_cache(
        cache, url, CACHE_TTL_QUALIFYING, lambda: busca_json(url), logger, "Última classificação"
    )
    if data is None:
        return None

    corridas = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
    return corridas[0] if corridas else None
