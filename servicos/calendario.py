import logging

from diskcache import Cache
from config import CACHE_DIRECTORY, CACHE_TTL_CALENDAR
from servicos.http_client import busca_json


cache = Cache(CACHE_DIRECTORY)
logger = logging.getLogger(__name__)


async def pega_calendario():
    url = "https://api.jolpi.ca/ergast/f1/current.json"
    data = cache.get(url)

    if data is not None:
        logger.debug("Calendário obtido do cache")
    else:
        data = await busca_json(url)
        if data is None:
            return None
        cache.set(url, data, expire=CACHE_TTL_CALENDAR)
        logger.info("Calendário atualizado pela API")

    return data["MRData"]["RaceTable"]["Races"]
