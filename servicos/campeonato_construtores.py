import logging

from diskcache import Cache
from datetime import datetime
from config import CACHE_DIRECTORY, CACHE_TTL_STANDINGS
from servicos.cache_fallback import buscar_com_cache
from servicos.http_client import busca_json

cache = Cache(CACHE_DIRECTORY)
logger = logging.getLogger(__name__)

async def campeonato_construtores():
    ano_atual = datetime.now().year
    url = f"https://api.jolpi.ca/ergast/f1/{ano_atual}/constructorstandings/"
    data = await buscar_com_cache(
        cache, url, CACHE_TTL_STANDINGS, lambda: busca_json(url), logger, "Classificação de construtores"
    )
    if data is None:
        return None

    times = data['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']

    return times
