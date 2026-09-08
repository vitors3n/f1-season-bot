from diskcache import Cache
from datetime import datetime
from config import CACHE_DIRECTORY, CACHE_TTL_STANDINGS
from servicos.http_client import busca_json

cache = Cache(CACHE_DIRECTORY)

async def campeonato_construtores():
    ano_atual = datetime.now().year
    url = f"https://api.jolpi.ca/ergast/f1/{ano_atual}/constructorstandings/"
    data = cache.get(url)
    
    if data is not None:
        print('~ Usando cache ~')
    else:
        data = await busca_json(url)
        if data is None:
            return None
        cache.set(url, data, expire=CACHE_TTL_STANDINGS)
        print('~ Usando API ~')
    
    # Bloco para quando não for possível acessar a API e não existir cache
    if data is None:
        return None

    times = data['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']

    return times
