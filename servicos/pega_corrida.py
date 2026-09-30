import logging

from modelos.corrida import Corrida
from diskcache import Cache
from config import CACHE_DIRECTORY, CACHE_TTL_NEXT_RACE
from servicos.cache_fallback import buscar_com_cache
from servicos.http_client import busca_json

cache = Cache(CACHE_DIRECTORY)
logger = logging.getLogger(__name__)

async def pega_corrida():
    url = "https://api.jolpi.ca/ergast/f1/current/next.json"
    data = await buscar_com_cache(
        cache, url, CACHE_TTL_NEXT_RACE, lambda: busca_json(url), logger, "Próxima corrida"
    )
    if data is None:
        return None

    corrida = data['MRData']['RaceTable']['Races'][0]

    proxima_corrida = Corrida(corrida)
    return proxima_corrida
