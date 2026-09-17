import logging

from diskcache import Cache
from datetime import datetime
from config import CACHE_DIRECTORY, CACHE_TTL_STANDINGS
from servicos.http_client import busca_json

cache = Cache(CACHE_DIRECTORY)
logger = logging.getLogger(__name__)

async def campeonato_pilotos():
    ano_atual = datetime.now().year
    url = f"https://api.jolpi.ca/ergast/f1/{ano_atual}/driverstandings/"
    data = cache.get(url)
    
    if data is not None:
        logger.debug("Classificação de pilotos obtida do cache")
    else:
        data = await busca_json(url)
        if data is None:
            return None
        cache.set(url, data, expire=CACHE_TTL_STANDINGS)
        logger.info("Classificação de pilotos atualizada pela API")

    # Bloco para quando não for possível acessar a API e não existir cache
    if data is None:
        return None

    corredores = data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']

    return corredores
