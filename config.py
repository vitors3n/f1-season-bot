import os

from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "America/Fortaleza")
TIMEZONE_LABEL = os.getenv("TIMEZONE_LABEL", "Fortaleza (CE)")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/lembretes.sqlite")
SETTINGS_DATABASE_PATH = os.getenv("SETTINGS_DATABASE_PATH", "data/configuracoes.sqlite")
CACHE_DIRECTORY = os.getenv("CACHE_DIRECTORY", "jolpi_cache")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

CACHE_TTL_NEXT_RACE = int(os.getenv("CACHE_TTL_NEXT_RACE", str(12 * 60 * 60)))
CACHE_TTL_CALENDAR = int(os.getenv("CACHE_TTL_CALENDAR", str(12 * 60 * 60)))
CACHE_TTL_STANDINGS = int(os.getenv("CACHE_TTL_STANDINGS", str(30 * 60)))
CACHE_TTL_QUALIFYING = int(os.getenv("CACHE_TTL_QUALIFYING", str(30 * 60)))
CACHE_TTL_WEATHER = int(os.getenv("CACHE_TTL_WEATHER", str(30 * 60)))

REMINDER_MINUTES = tuple(
    int(minutes.strip())
    for minutes in os.getenv("REMINDER_MINUTES", "10,5").split(",")
    if minutes.strip()
)
