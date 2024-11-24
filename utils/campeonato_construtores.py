from diskcache import Cache
import requests

url = "https://api.jolpi.ca/ergast/f1/2024/constructorstandings/"
cache = Cache('jolpi_cache')

def campeonato_construtores():
    data = cache.get(url)
    
    if data is not None:
        print('~ Usando cache ~')
    else:
        response = requests.get(url)
        print('~ Usando API ~')
        if response.status_code == 200:
            data = response.json()
            cache.set(url, data, expire=30*60)

    times = data['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']

    return times