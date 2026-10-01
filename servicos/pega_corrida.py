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

    try:
        corridas = data["MRData"]["RaceTable"]["Races"]
        corrida = corridas[0]
        return Corrida(corrida)
    except (AttributeError, IndexError, KeyError, TypeError, ValueError):
        logger.warning("Resposta inválida da API ao buscar a próxima corrida")
        return None
