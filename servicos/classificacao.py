from diskcache import Cache
from config import CACHE_DIRECTORY, CACHE_TTL_QUALIFYING
from servicos.http_client import busca_json


cache = Cache(CACHE_DIRECTORY)


async def pega_ultima_classificacao():
    url = "https://api.jolpi.ca/ergast/f1/current/last/qualifying.json"
    data = cache.get(url)

    if data is not None:
        print("~ Usando cache ~")
    else:
        data = await busca_json(url)
        if data is None:
            return None
        cache.set(url, data, expire=CACHE_TTL_QUALIFYING)
        print("~ Usando API ~")

    corridas = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
    return corridas[0] if corridas else None
