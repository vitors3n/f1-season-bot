from diskcache import Cache
from datetime import datetime
import requests
from config import CACHE_DIRECTORY, CACHE_TTL_STANDINGS, REQUEST_TIMEOUT

cache = Cache(CACHE_DIRECTORY)

def campeonato_pilotos():
    ano_atual = datetime.now().year
    url = f"https://api.jolpi.ca/ergast/f1/{ano_atual}/driverstandings/"
    data = cache.get(url)
    
    if data is not None:
        print('~ Usando cache ~')
    else:
        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            cache.set(url, data, expire=CACHE_TTL_STANDINGS)
            print('~ Usando API ~')
        except (requests.RequestException, ValueError):
            return None

    # Bloco para quando não for possível acessar a API e não existir cache
    if data is None:
        return None

    corredores = data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']

    return corredores
