from datetime import datetime

from diskcache import Cache
import pytz
from config import CACHE_DIRECTORY, CACHE_TTL_WEATHER
from servicos.http_client import busca_json


cache = Cache(CACHE_DIRECTORY)


async def pega_previsao(latitude, longitude):
    cache_key = f"weather:{latitude}:{longitude}"
    data = cache.get(cache_key)

    if data is not None:
        print("~ Usando cache ~")
        return data

    parametros = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": (
            "temperature_2m,precipitation_probability,weather_code,"
            "wind_speed_10m"
        ),
        "forecast_days": 16,
        "timezone": "UTC",
    }

    data = await busca_json(
        "https://api.open-meteo.com/v1/forecast",
        params=parametros,
    )
    if data is None:
        return None
    cache.set(cache_key, data, expire=CACHE_TTL_WEATHER)
    print("~ Usando API ~")
    return data


def previsao_no_horario(previsao, dia_hora):
    horas = previsao.get("hourly", {})
    datas = horas.get("time", [])
    if not datas:
        return None

    instantes = [
        datetime.fromisoformat(data).replace(tzinfo=pytz.UTC)
        for data in datas
    ]
    alvo = dia_hora.astimezone(pytz.UTC)

    if alvo < instantes[0] or alvo > instantes[-1]:
        return None

    indice = min(
        range(len(instantes)),
        key=lambda item: abs((instantes[item] - alvo).total_seconds()),
    )
    return {
        "temperatura": horas["temperature_2m"][indice],
        "chance_chuva": horas["precipitation_probability"][indice],
        "codigo": horas["weather_code"][indice],
        "vento": horas["wind_speed_10m"][indice],
    }
