from modelos.corrida import Corrida
from diskcache import Cache
import requests
from config import CACHE_DIRECTORY, CACHE_TTL_NEXT_RACE, REQUEST_TIMEOUT

cache = Cache(CACHE_DIRECTORY)

def pega_corrida():
    url = "https://api.jolpi.ca/ergast/f1/current/next.json"
    data = cache.get(url)
    
    if data is not None:
        print('~ Usando cache ~')
    else:
        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            cache.set(url, data, expire=CACHE_TTL_NEXT_RACE)
            print('~ Usando API ~')
        except (requests.RequestException, ValueError):
            return None

    # Bloco para quando não for possível acessar a API e não existir cache
    if data is None:
        return None

    corrida = data['MRData']['RaceTable']['Races'][0]

    proxima_corrida = Corrida(corrida)
    return proxima_corrida
