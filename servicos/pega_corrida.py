from modelos.corrida import Corrida
from diskcache import Cache
from config import CACHE_DIRECTORY, CACHE_TTL_NEXT_RACE
from servicos.http_client import busca_json

cache = Cache(CACHE_DIRECTORY)

async def pega_corrida():
    url = "https://api.jolpi.ca/ergast/f1/current/next.json"
    data = cache.get(url)
    
    if data is not None:
        print('~ Usando cache ~')
    else:
        data = await busca_json(url)
        if data is None:
            return None
        cache.set(url, data, expire=CACHE_TTL_NEXT_RACE)
        print('~ Usando API ~')

    # Bloco para quando não for possível acessar a API e não existir cache
    if data is None:
        return None

    corrida = data['MRData']['RaceTable']['Races'][0]

    proxima_corrida = Corrida(corrida)
    return proxima_corrida
