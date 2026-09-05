from diskcache import Cache
import requests


cache = Cache("jolpi_cache")


def pega_ultima_classificacao():
    url = "https://api.jolpi.ca/ergast/f1/current/last/qualifying.json"
    data = cache.get(url)

    if data is not None:
        print("~ Usando cache ~")
    else:
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            cache.set(url, data, expire=30 * 60)
            print("~ Usando API ~")
        except (requests.RequestException, ValueError):
            return None

    corridas = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
    return corridas[0] if corridas else None
