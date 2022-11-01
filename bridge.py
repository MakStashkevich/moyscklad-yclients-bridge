import asyncio
import logging
import sys

from database.database import bind_database
from handler.moyscklad_handler import MoysckladHandler
from handler.yclients_handler import YClientsHandler
from request.api import ApiException
from settings import get_global_settings

logging.basicConfig(
    level=logging.INFO if not get_global_settings().is_debug else logging.DEBUG,
    format='[%(asctime)s][%(name)s][%(levelname)s]: %(message)s'
)
_logger = logging.getLogger(__name__)


class Bridge:
    yclients_handler: YClientsHandler
    moysclad_handler: MoysckladHandler

    def __init__(self):
        asyncio.run(self.process())

    async def process(self):
        await bind_database()

        self.yclients_handler = YClientsHandler()
        self.moysclad_handler = MoysckladHandler()

        try:
            await self.yclients_handler.connect()
            await self.moysclad_handler.connect()
        except (ApiException, Exception) as ex:
            message = ex.message if isinstance(ex, ApiException) else str(ex)
            _logger.error(f"Not connected: {message}")
            if get_global_settings().is_debug:
                _logger.exception(ex)
            sys.exit(1)


if __name__ == '__main__':
    try:
        Bridge()
    except KeyboardInterrupt:
        pass
