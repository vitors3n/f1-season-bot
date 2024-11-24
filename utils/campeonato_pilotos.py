from diskcache import Cache
from datetime import datetime
import requests

cache = Cache('jolpi_cache')

def campeonato_pilotos():
    ano_atual = datetime.now().year
    url = f"https://api.jolpi.ca/ergast/f1/{ano_atual}/driverstandings/"
    data = cache.get(url)
    
    if data is not None:
        print('~ Usando cache ~')
    else:
        response = requests.get(url)
        print('~ Usando API ~')
        if response.status_code == 200:
            data = response.json()
            cache.set(url, data, expire=30*60)

    corredores = data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']

    return corredores
