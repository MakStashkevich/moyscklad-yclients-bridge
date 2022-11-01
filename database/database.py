import asyncio
import logging
from datetime import datetime

from pony.orm import *

from settings import get_database_settings

_logger = logging.getLogger(__name__)

database = Database()
settings = get_database_settings()


class YClientsData(database.Entity):
    id = PrimaryKey(int, size=64, auto=True)
    company_id = Required(int, default=0)  # Номер компании для синхронизации
    storage_id = Required(int, default=0)  # Номер склада для синхронизации
    access_token = Optional(str, default="")  # Токен пользователя
    created_at = Required(datetime, default=lambda: datetime.now())
    updated_at = Required(datetime, default=lambda: datetime.now())


class MoyscladData(database.Entity):
    id = PrimaryKey(int, size=64, auto=True)
    access_token = Required(str)  # Токен пользователя
    receipt_id = Required(int, default=1, min=1)  # Номер оприходования товаров
    created_at = Required(datetime, default=lambda: datetime.now())
    updated_at = Required(datetime, default=lambda: datetime.now())


def is_connected_database() -> bool:
    return database.provider is not None


async def bind_database():
    if is_connected_database():
        return

    while not is_connected_database():
        try:
            database.bind(
                provider='sqlite',
                filename=settings.database_filename,
                create_db=True
            )
            database.generate_mapping(create_tables=True)
            _logger.info('Database generated mapping successful')
        except OperationalError as ex:
            _logger.error(f'Not bind to Database ({ex})...')
            _logger.error(f'Paused on 5 seconds before reconnect ...')
            await asyncio.sleep(5)
