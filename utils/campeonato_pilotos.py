from diskcache import Cache
import requests

url = "https://api.jolpi.ca/ergast/f1/2024/driverstandings/"
cache = Cache('jolpi_cache')

def campeonato_pilotos():
    data = cache.get(url)
    
    if data is not None:
        print('~ Usando cache ~')
    else:
        response = requests.get(url)
        print('~ Usando API ~')
        if response.status_code == 200:
            data = response.json()
            cache.set(url, data, expire=10*24*60*60)

    corredores = data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']

    return corredores
