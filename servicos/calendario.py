from diskcache import Cache
import requests


cache = Cache("jolpi_cache")


def pega_calendario():
    url = "https://api.jolpi.ca/ergast/f1/current.json"
    data = cache.get(url)

    if data is not None:
        print("~ Usando cache ~")
    else:
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            cache.set(url, data, expire=12 * 60 * 60)
            print("~ Usando API ~")
        except (requests.RequestException, ValueError):
            return None

    return data["MRData"]["RaceTable"]["Races"]
