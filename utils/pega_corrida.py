from utils.corrida_passou import corrida_passou
from modelos.corrida import Corrida
from datetime import datetime
from diskcache import Cache
import requests

cache = Cache('jolpi_cache')

def pega_corrida():
    ano_atual = datetime.now().year
    url = f"https://api.jolpi.ca/ergast/f1/{ano_atual}/"
    # nova_url = https://api.jolpi.ca/ergast/f1/current/next.json
    data = cache.get(url)
    
    if data is not None:
        print('~ Usando cache ~')
    else:
        response = requests.get(url)
        print('~ Usando API ~')
        if response.status_code == 200:
            data = response.json()
            cache.set(url, data, expire=12*60*60)

    corridas = data['MRData']['RaceTable']['Races']

    proxima_corrida_json = ''
 
    for corrida in corridas:
        if not corrida_passou(f"{corrida['date']} {corrida['time']}"):
            proxima_corrida_json = corrida
            break

    proxima_corrida = Corrida(proxima_corrida_json)
    return proxima_corrida
