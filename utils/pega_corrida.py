from utils.corrida_passou import corrida_passou
from modelos.corrida import Corrida
from datetime import datetime
from diskcache import Cache
import requests

cache = Cache('jolpi_cache')

def pega_corrida():
    url = "https://api.jolpi.ca/ergast/f1/current/next.json"
    data = cache.get(url)
    
    if data is not None:
        print('~ Usando cache ~')
    else:
        response = requests.get(url)
        print('~ Usando API ~')
        if response.status_code == 200:
            data = response.json()
            cache.set(url, data, expire=12*60*60)

    proxima_corrida = Corrida(data)
    return proxima_corrida
