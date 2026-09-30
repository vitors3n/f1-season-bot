import logging

from diskcache import Cache
from config import CACHE_DIRECTORY, CACHE_TTL_CALENDAR
from servicos.cache_fallback import buscar_com_cache
from servicos.http_client import busca_json


cache = Cache(CACHE_DIRECTORY)
logger = logging.getLogger(__name__)


async def pega_calendario():
    url = "https://api.jolpi.ca/ergast/f1/current.json"
    data = await buscar_com_cache(
        cache, url, CACHE_TTL_CALENDAR, lambda: busca_json(url), logger, "Calendário"
    )
    if data is None:
        return None

    return data["MRData"]["RaceTable"]["Races"]
