import os
import zoneinfo
from functools import lru_cache
from secrets import token_hex

from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class GlobalSettings(BaseSettings):
    is_debug: bool = False
    is_trace_requests: bool = False
    delay_requests: int = 3000  # milliseconds (3 sec)
    delay_cache: int = 120000  # milliseconds (2 min)
    attempts_requests: int = 6  # try
    timeout_requests: int = 10  # seconds
    timezone: str = "Europe/Moscow"
    language: str = "ru-RU"


@lru_cache()
def get_global_settings():
    return GlobalSettings()


@lru_cache()
def get_timezone():
    return zoneinfo.ZoneInfo(key=get_global_settings().timezone)


class YClientsSettings(BaseSettings):
    yclients_api_partner_token: str = None
    yclients_api_user_token: str = None
    yclients_webhook_set: bool = False
    yclients_login: str = None
    yclients_password: str = None
    yclients_company_name: str = None
    yclients_storage_name: str = None


@lru_cache()
def get_yclients_settings():
    return YClientsSettings()


class MoyscladSettings(BaseSettings):
    moysclad_login: str = None
    moysclad_password: str = None


@lru_cache()
def get_moysclad_settings():
    return MoyscladSettings()


class SqliteSettings(BaseSettings):
    database_filename: str = "bridge.session"


@lru_cache()
def get_database_settings():
    settings = SqliteSettings()
    settings.database_filename = "/".join([os.path.abspath(os.getcwd()), settings.database_filename])
    return settings


class WebserverSettings(BaseSettings):
    webserver_session_secret: str = token_hex()
    webserver_host: str = "localhost"
    webserver_port: int = 80


@lru_cache()
def get_webserver_settings():
    return WebserverSettings()