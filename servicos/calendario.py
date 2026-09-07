from diskcache import Cache
import requests
from config import CACHE_DIRECTORY, CACHE_TTL_CALENDAR, REQUEST_TIMEOUT


cache = Cache(CACHE_DIRECTORY)


def pega_calendario():
    url = "https://api.jolpi.ca/ergast/f1/current.json"
    data = cache.get(url)

    if data is not None:
        print("~ Usando cache ~")
    else:
        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            cache.set(url, data, expire=CACHE_TTL_CALENDAR)
            print("~ Usando API ~")
        except (requests.RequestException, ValueError):
            return None

    return data["MRData"]["RaceTable"]["Races"]
